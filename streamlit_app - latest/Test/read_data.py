import streamlit as st
import datatable as dt

df = dt.Frame(r"C:\Users\gagan\Downloads\dataraft_greywiz_datapath\Austin1\Austin1.jay").to_pandas()

st.dataframe(df)