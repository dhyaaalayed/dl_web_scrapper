from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago
from airflow.operators.dagrun_operator import TriggerDagRunOperator




default_args = {
    'owner': 'Dieaa',
    'start_date': days_ago(0),
    'email': [],
    'email_on_failure': False,
    'email_on_retry': False,
    'schedule_interval': '@daily',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


json_dag = DAG(
    dag_id='json_main_dag',
    default_args=default_args,
    description='Updating Excels',
    schedule_interval='0 0 * * *',
)



json_main = BashOperator(
    task_id='json_main_task',
    bash_command='cd /app && python3 mg_json_main.py',
    dag=json_dag,
)







json_main










