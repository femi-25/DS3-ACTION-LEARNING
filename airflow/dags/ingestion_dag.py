from pendulum import datetime
from pathlib import Path
import subprocess
import duckdb

from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.providers.postgres.hooks.postgres import PostgresHook  # if you're logging stats
from airflow.operators.python import PythonOperator
from modules.gxe_ingestion_stats.gx_stats import parse_gxe_output  # your custom parser

from great_expectations import ExpectationSuite
import great_expectations.expectations as gxe
from great_expectations_provider.operators.validate_dataframe import GXValidateDataFrameOperator

# ─── Expectation Suite ───────────────────────────────────────────────

EXPECTED_COLUMNS = [
    "age", "height_cm", "weight_kg", "potential", "weak_foot", "skill_moves",
    "pace", "shooting", "passing", "dribbling", "defending", "physic",
    "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy",
    "attacking_short_passing", "attacking_volleys", "skill_dribbling",
    "skill_curve", "skill_fk_accuracy", "skill_long_passing", "skill_ball_control",
    "movement_acceleration", "movement_sprint_speed", "movement_agility",
    "movement_reactions", "movement_balance", "power_shot_power", "power_jumping",
    "power_stamina", "power_strength", "power_long_shots", "mentality_aggression",
    "mentality_interceptions", "mentality_positioning", "mentality_vision",
    "mentality_penalties", "mentality_composure", "defending_standing_tackle",
    "defending_sliding_tackle",
    "preferred_foot", "main_position", "att_work_rate", "def_work_rate", "nationality_grouped"
]

expectation_suite = ExpectationSuite(
    name="player_data_validation",
    expectations=[
        gxe.ExpectTableColumnCountToEqual(value=len(EXPECTED_COLUMNS)),
        gxe.ExpectTableColumnsToMatchSet(column_set=EXPECTED_COLUMNS),
        gxe.ExpectColumnValuesToBeInSet(column="preferred_foot", value_set=["Left", "Right"]),
        gxe.ExpectColumnValuesToBeInSet(column="main_position", value_set=["GK","CB","LB","RB","CM","CDM","CAM","LW","RW","ST"]),
        gxe.ExpectColumnValuesToBeInSet(column="att_work_rate", value_set=["Low","Medium","High"]),
        gxe.ExpectColumnValuesToBeInSet(column="def_work_rate", value_set=["Low","Medium","High"]),
        gxe.ExpectColumnValuesToBeInSet(column="nationality_grouped", value_set=["Argentina","Brazil","Portugal","Poland","Other"]),
        gxe.ExpectColumnValuesToBeBetween(column="age", min_value=16, max_value=40),
        gxe.ExpectColumnValuesToBeBetween(column="height_cm", min_value=160, max_value=200),
        gxe.ExpectColumnValuesToBeBetween(column="weight_kg", min_value=55, max_value=100),
        gxe.ExpectColumnValuesToBeBetween(column="potential", min_value=50, max_value=95),
        gxe.ExpectColumnValuesToBeBetween(column="weak_foot", min_value=1, max_value=5),
        gxe.ExpectColumnValuesToBeBetween(column="skill_moves", min_value=1, max_value=5),
        gxe.ExpectColumnValuesToBeOfType(column="pace", type_="float"),
        gxe.ExpectColumnValuesToMatchRegex(column="pace", regex=r"^\d+(\.\d+)?$"),
        *[gxe.ExpectColumnValuesToNotBeNull(column=col) for col in EXPECTED_COLUMNS],
    ]
)

# ─── DAG Definition ───────────────────────────────────────────────────

with DAG(
    dag_id="ingestion_dag",
    schedule_interval="*/1 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["gnn", "ingestion"],
) as dag:

    @task()
    def read_data():
        raw_dir = Path("/opt/airflow/data/raw_data")
        if list(raw_dir.glob("*.csv")):
            selected_file = subprocess.getoutput("bash $AIRFLOW_HOME/scripts/shell/random_file.sh").strip()
            duckdb.connect("ingest.ddb").execute(
                f"CREATE OR REPLACE TABLE latest AS SELECT * FROM read_csv_auto('{selected_file}', nullstr='');"
            )
            return selected_file
        else:
            raise AirflowSkipException("No CSV files found in raw_data")

    def retrieve_df_for_gx_validation():
        try:
            return duckdb.connect("ingest.ddb").execute("SELECT * FROM latest").fetchdf()
        except duckdb.CatalogException:
            return 0

    validate_data = GXValidateDataFrameOperator(
        task_id="validate_data",
        configure_dataframe=retrieve_df_for_gx_validation,
        expect=expectation_suite,
        context_type="ephemeral",
        result_format="COMPLETE"
    )
    @task()
    def save_file(ti):
        import duckdb

        conn = duckdb.connect("ingest.ddb")
        df = conn.execute("SELECT * FROM latest").fetchdf()

        file_path = ti.xcom_pull(task_ids="read_data", key="return_value")
        file_name = Path(file_path).name
        good_path = f"/opt/airflow/data/good_data/{file_name}"
        bad_path = f"/opt/airflow/data/bad_data/bad_{file_name}"

        gx_output = ti.xcom_pull(task_ids="validate_data", key="return_value")
        success = gx_output["success"]
        column_check_passed = any(
            r["expectation_type"] == "expect_table_columns_to_match_set" and r["success"]
            for r in gx_output["expectations"]
        )

        if success and column_check_passed:
            conn.execute(f"COPY (SELECT * FROM latest) TO '{good_path}' (HEADER, DELIMITER ',');")
            return

        if column_check_passed:
            bad_rows = set()
            for r in gx_output["expectations"]:
                if not r["success"]:
                    idxs = r.get("result", {}).get("unexpected_index_list", [])
                    bad_rows |= set(idxs)

            if bad_rows:
                ids = ", ".join(str(i) for i in sorted(bad_rows))
                conn.execute(f"""
                    COPY (
                        WITH tmp AS (SELECT *, row_number() OVER () - 1 AS rn FROM latest)
                        SELECT * EXCLUDE rn FROM tmp WHERE rn IN ({ids})
                    ) TO '{bad_path}' (HEADER, DELIMITER ',');
                """)
                conn.execute(f"""
                    COPY (
                        WITH tmp AS (SELECT *, row_number() OVER () - 1 AS rn FROM latest)
                        SELECT * EXCLUDE rn FROM tmp WHERE rn NOT IN ({ids})
                    ) TO '{good_path}' (HEADER, DELIMITER ',');
                """)
                return

        conn.execute(f"COPY (SELECT * FROM latest) TO '{bad_path}' (HEADER, DELIMITER ',');")

    _read = read_data()
    _save = save_file()
    _read >> validate_data >> _save
