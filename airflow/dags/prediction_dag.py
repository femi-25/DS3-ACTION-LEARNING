import pendulum
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException, AirflowException, AirflowFailException

def _check_for_new_data(ti):
    from pathlib import Path

    folder = Path('/opt/airflow/data/good_data')
    checklist = folder / 'prediction_checklist.txt'
    files = list(folder.glob('*.csv'))

    if not files:
        raise AirflowSkipException("No good_data files found")

    if not checklist.exists():
        checklist.touch()

    with open(checklist, 'r') as f:
        processed = set(line.strip() for line in f)

    new_files = [str(file) for file in files if str(file) not in processed]

    if new_files:
        ti.xcom_push(key='predict_new_files', value=new_files)
    else:
        raise AirflowSkipException("No new good_data files to predict")

def _make_predictions(ti):
    import duckdb
    import requests
    import pandas as pd
    from pathlib import Path
    import os
    import json
    from airflow.hooks.base import BaseHook

    def handle_200(new_files):
        with open('/opt/airflow/data/good_data/prediction_checklist.txt', 'a') as f:
            for file in new_files:
                f.write(file + '\n')

    def handle_400():
        raise AirflowFailException("Bad request (400/422)")

    def handle_500():
        raise AirflowException("Server error (500)")

    # Load files
    new_files = ti.xcom_pull(task_ids='check_for_new_data', key='predict_new_files')
    quoted = ', '.join(f"'{path}'" for path in new_files)

    conn = duckdb.connect()
    df = conn.execute(f"SELECT * FROM read_csv_auto([{quoted}]);").fetchdf()

    payload = { "features": df.to_dict(orient="records") }

    app_conn = BaseHook.get_connection("http_conn_fastapi")
    url = f"http://host.docker.internal:8000/predict"
    response = requests.post(url, json=payload)

    # Handle response
    handlers = {
        200: lambda: (
            handle_200(new_files),
            save_predictions(df, response.json(), new_files)
        ),
        400: handle_400,
        422: handle_400,
        500: handle_500,
    }

    handler = handlers.get(response.status_code)
    if handler:
        handler()
    else:
        print(f"Unknown status code: {response.status_code}")

def save_predictions(df, predictions, input_files):
    import pandas as pd
    from pathlib import Path

    # Ensure destination directory exists
    Path("/opt/airflow/data/predicted_data").mkdir(parents=True, exist_ok=True)

    if isinstance(predictions, dict): predictions = [predictions]  # single record handling

    overall_scores = [p.get("predicted_overall") for p in predictions]
    df["predicted_overall"] = overall_scores

    # Save one output per input file
    for input_path in input_files:
        name = Path(input_path).name
        out_path = Path("/opt/airflow/data/predicted_data") / f"predicted_{name}"
        df.to_csv(out_path, index=False)
        print(f"✅ Saved prediction: {out_path}")

# DAG configuration
args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id="prediction_dag",
    schedule="*/2 * * * *",
    start_date=pendulum.now().subtract(minutes=2),
    catchup=False,
    max_active_runs=1,
    default_args=args,
) as dag:

    check_for_new_data = PythonOperator(
        task_id="check_for_new_data",
        python_callable=_check_for_new_data
    )

    make_predictions = PythonOperator(
        task_id="make_predictions",  # ✅ fixed name
        python_callable=_make_predictions
    )

    check_for_new_data >> make_predictions