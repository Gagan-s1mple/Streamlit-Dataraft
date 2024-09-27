import os
import datatable as dt
import duckdb
import glob
import os
import datatable as dt
import streamlit as st
from celery import Celery as cl
#below are the codes to look into every subfolder and merge, create .jay and duckdb files
# def merge_csv_files(parent_folder):
#     for root, dirs, files in os.walk(parent_folder):
#         for directory in dirs:
#             folder_path = os.path.join(root, directory)
#             csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
            
#             if csv_files:
#                 if len(csv_files) > 1:
#                     merged_dt = None
#                     for file in csv_files:
#                         file_path = os.path.join(folder_path, file)
#                         df = dt.fread(file_path)
#                         if merged_dt is None:
#                             merged_dt = df.copy()
#                         else:
#                             merged_dt.rbind(df)
#                     output_file = os.path.join(folder_path, f"{directory}.csv")
#                     merged_dt.to_csv(output_file)
#                     print(f"Merged CSV files in '{folder_path}' saved to '{output_file}'.")
#                 else:
#                     print(f"Skipping deletion in '{folder_path}' as only one CSV file exists.")


# #To convert csv to .jay
# def convert_to_jay(parent_folder):
#     for subdir, dirs, files in os.walk(parent_folder):
#         for file in files:
#             if file.endswith('.csv'):
#                 csv_path = os.path.join(subdir, file)
#                 df = dt.fread(csv_path)
#                 output_path = os.path.join(subdir, os.path.splitext(file)[0] + '.jay')
#                 df.to_jay(output_path)
#                 print(f"Converted {csv_path} to {output_path}")

# #To create duckdb file
# def create_duckdb_files(parent_folder):
#     for subdir, dirs, files in os.walk(parent_folder):
#         csv_files = [f for f in files if f.endswith('.csv')]
#         if csv_files:
#             db_path = os.path.join(subdir, f"{os.path.basename(subdir)}.duckdb")
#             if not os.path.exists(db_path):
#                 conn = duckdb.connect(db_path)
#                 csv_path = os.path.join(subdir, csv_files[0])
#                 table_name = os.path.splitext(csv_files[0])[0]
#                 conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")
#         else:
#             print(f"No CSV file found in {subdir}")



#below are the codes to execute the above functions for the parent directory without going to any subfolders
app=cl('tasks',broker='redis://localhost:6379/0')
@app.task
def merge_csv_to_jay_to_duckdb(parent_folder):
    #checking csv files in the folder
    csv_files = [file for file in os.listdir(parent_folder) if file.endswith('.csv')]
    if not csv_files:
        print(f"No CSV file found in {parent_folder}")
        return
    #merging dataframe
    merged_dt = None
    for file in csv_files:
        file_path = os.path.join(parent_folder, file)
        df = dt.fread(file_path)
        #merged_dt is initially None. After the first loop, it is merged using rbind
        if merged_dt is None:
            merged_dt = df.copy()
        else:
            merged_dt.rbind(df,force=True)

    dataset_name = os.path.basename(parent_folder)
    output_file = os.path.join(parent_folder, f"{dataset_name}.csv")
    merged_dt.to_csv(output_file)
    merged_dt.to_jay(f'{parent_folder}/{dataset_name}.jay')#Creating .jay file from the datatable

    db_path = os.path.join(parent_folder, f"{dataset_name}.duckdb")
    if not os.path.exists(db_path):
        conn = duckdb.connect(db_path)
        conn.execute(f"CREATE TABLE {dataset_name} AS SELECT * FROM read_csv_auto('{output_file}')")
    else:
        print(f"DuckDB database already exists at {db_path}")