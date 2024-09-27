import os
import datatable as dt
import duckdb
from celery import Celery as cl

app=cl('tasks',broker='redis://localhost:6379/0')
@app.task
def csv_to_jay_to_duckdb(parent_folder):
    dataset_name = os.path.basename(parent_folder)
    csv_path=f"{parent_folder}/{dataset_name}.csv"
    
    df = dt.fread(f"{parent_folder}/{dataset_name}.csv")
    jay_file_path = f'{parent_folder}/{dataset_name}.jay'
    df.to_jay(f'{parent_folder}/{dataset_name}.jay')

    db_path = os.path.join(parent_folder, f"{dataset_name}.duckdb")
    if os.path.exists(db_path):
        os.remove(db_path)
    if not os.path.exists(db_path):
        conn = duckdb.connect(db_path)
        conn.execute(f"CREATE TABLE {dataset_name} AS SELECT * FROM read_csv_auto('{csv_path}')")
    else:
        print(f"DuckDB database already exists at {db_path}")