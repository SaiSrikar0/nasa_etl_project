from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# DAG defaults
default_args = {
	"owner": "airflow",
	"depends_on_past": False,
	"email_on_failure": False,
	"email_on_retry": False,
	"retries": 1,
	"retry_delay": timedelta(minutes=5),
}

with DAG(
	dag_id="nasa_etl_pipeline",
	default_args=default_args,
	description="ETL pipeline for NASA APOD data",
	schedule_interval="@daily",
	start_date=datetime(2025, 12, 1),
	catchup=False,
) as dag:

	# Extract: calls scripts/extract.py to fetch NASA data and write to data/raw
	extract_task = BashOperator(
		task_id="extract_nasa_data",
		bash_command="python /opt/airflow/scripts/extract.py",
		env={
			"PYTHONUNBUFFERED": "1",
			# Pass through env variables if needed inside the script
			"api_key": "{{ var.value.api_key if var.value.api_key else '' }}",
		},
	)

	# Transform: reads raw JSON and writes staged CSV
	transform_task = BashOperator(
		task_id="transform_nasa_data",
		bash_command="python /opt/airflow/scripts/transform.py",
		env={
			"PYTHONUNBUFFERED": "1",
		},
	)

	# Load: loads staged CSV to Supabase
	load_task = BashOperator(
		task_id="load_to_supabase",
		bash_command="python /opt/airflow/scripts/load.py",
		env={
			"PYTHONUNBUFFERED": "1",
			"supabase_url": "{{ var.value.supabase_url if var.value.supabase_url else '' }}",
			"supabase_key": "{{ var.value.supabase_key if var.value.supabase_key else '' }}",
		},
	)

	extract_task >> transform_task >> load_task
