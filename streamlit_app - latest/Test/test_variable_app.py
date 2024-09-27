import streamlit as st
import pandas as pd
import random
import datatable as dt

jay_present = st.session_state.get('jay_present',True)
dataset_path=r"C:\Users\gagan\Downloads\test"
dataset_name="my_dataset.csv"
if not jay_present:        
    table=dt.fread(f'{dataset_path}/{dataset_name}')
    table.to_jay(f'{dataset_path}/my_dataaset.jay')

def insert_variable(df):
    df[f'new_variable_{random.randint(1,1000)}']=random.randint(1,1000)
    new_table = dt.Frame(df)
    new_table.to_jay(f'{dataset_path}/my_dataaset.jay')
    #st.dataframe(new_table.to_pandas())
df = dt.Frame(f'{dataset_path}/my_dataaset.jay').to_pandas()


st.dataframe(df)
#uploaded_file = st.file_uploader("Choose a CSV file", accept_multiple_files=False)

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)
#     st.dataframe(df)
addvar = st.button("Add a variable")


if addvar:
    insert_variable(df)
