random_file=$(cd $AIRFLOW_HOME/data/raw_data && shuf -e -n 1 $(realpath *.csv))
echo "$random_file"