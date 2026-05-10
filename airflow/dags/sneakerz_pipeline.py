from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'sneakerz',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

dag = DAG(
    dag_id='sneakerz_pipeline',
    description='Pipeline complet Sneakerz : Scraping → Bronze → Silver → Gold → PostgreSQL → MinIO',
    schedule_interval='0 * * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['sneakerz', 'bigdata', 'emsi'],
    default_args=default_args,
)

# ── 1. Scraping ───────────────────────────────────────────────
def run_scraping():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/scraper/spiders/real_scraper.py'],
        capture_output=True, text=True, cwd='/opt/airflow/scraper'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Scraping failed: {result.stderr}")

task_scraping = PythonOperator(
    task_id='scrape_footlocker',
    python_callable=run_scraping,
    dag=dag,
)

# ── 2. Bronze → Silver ────────────────────────────────────────
def run_silver():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/scraper/silver_transform.py'],
        capture_output=True, text=True, cwd='/opt/airflow/scraper'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Silver failed: {result.stderr}")

task_silver = PythonOperator(
    task_id='bronze_to_silver',
    python_callable=run_silver,
    dag=dag,
)

# ── 3. Silver → Gold ──────────────────────────────────────────
def run_gold():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/scraper/gold_analytics.py'],
        capture_output=True, text=True, cwd='/opt/airflow/scraper'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Gold failed: {result.stderr}")

task_gold = PythonOperator(
    task_id='silver_to_gold',
    python_callable=run_gold,
    dag=dag,
)

# ── 4. Gold → PostgreSQL ──────────────────────────────────────
def run_postgres():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/backend/load_data.py'],
        capture_output=True, text=True, cwd='/opt/airflow/backend'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"PostgreSQL failed: {result.stderr}")

task_postgres = PythonOperator(
    task_id='gold_to_postgres',
    python_callable=run_postgres,
    dag=dag,
)

# ── 5. Upload MinIO ───────────────────────────────────────────
def run_minio_upload():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/scraper/minio_upload.py'],
        capture_output=True, text=True, cwd='/opt/airflow/scraper'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"MinIO upload failed: {result.stderr}")

task_minio = PythonOperator(
    task_id='upload_to_minio',
    python_callable=run_minio_upload,
    dag=dag,
)

# ── 6. Quality Checks ─────────────────────────────────────────
def run_quality():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/scraper/quality_checks.py'],
        capture_output=True, text=True, cwd='/opt/airflow/scraper'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Quality checks failed: {result.stderr}")

task_quality = PythonOperator(
    task_id='quality_checks',
    python_callable=run_quality,
    dag=dag,
)

# ── 7. Logs ───────────────────────────────────────────────────
def run_logs():
    import subprocess
    result = subprocess.run(
        ['python', '/opt/airflow/scraper/logger.py'],
        capture_output=True, text=True, cwd='/opt/airflow/scraper'
    )
    print(result.stdout)

task_logs = PythonOperator(
    task_id='log_pipeline',
    python_callable=run_logs,
    dag=dag,
)

# ── Ordre d'exécution ─────────────────────────────────────────
task_scraping >> task_silver >> task_gold >> task_postgres >> task_minio >> task_quality >> task_logs