import streamlit as st
import streamlit_antd_components as sac

tran = sac.transfer(items=["Good","Bad"],pagination=True,return_index=False,titles=['good','bad'])