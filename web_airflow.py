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


web_dag = DAG(
    dag_id='web_main_dag',
    default_args=default_args,
    description='Scrapping from Telekom',
    schedule_interval=timedelta(days=1),
)


web_main = BashOperator(
    task_id='web_main_task',
    bash_command='cd /app && python3 mg_web_main.py',
    dag=web_dag,
)

trigger_self = TriggerDagRunOperator(
    task_id='repeat_web_main_task',
    trigger_dag_id=web_dag.dag_id,
    dag=web_dag
)


web_main >> trigger_self















