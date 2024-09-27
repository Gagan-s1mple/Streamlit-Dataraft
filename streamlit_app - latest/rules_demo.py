import streamlit as st
from streamlit_card import card
import streamlit_antd_components as sac
import pandas as pd
import numpy as np
import json

st.set_page_config(layout="wide",initial_sidebar_state='collapsed',)
st.markdown("""
            <style>
            .mantine-SegmentedControl-root {
                padding:0;
                margin:0;
                rotate: 30deg;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:nth-child(4) {
                margin-left:3rem;
            }
            
            </style>
""", unsafe_allow_html=True)

widget_id = (id for id in range(1, 10000))

estimates = json.load(open("./estimates.json"))
relationals = [">", "<", "==", "<=", ">="]
quantifiers = ["For all", "for any"]
numericals = st.session_state.get("numericals", [])
categoricals = st.session_state.get("categoricals", [])
conditions = st.session_state.get('conditions', [{"logical_op": "AND"}])
file_count = 0

def condition(item, i, next_exists=False):
    cols = st.columns([0.35,0.5,0.25,0.25,0.30,0.5,0.4,0.25])
    with cols[0]:
        item['estimate'] = st.selectbox(label="Fields", options=[item['name'] for item in estimates], key=next(widget_id))
    with cols[1]:
        item['numeric'] = st.selectbox(label="Numerics", options=numericals, key=next(widget_id))
    with cols[2]:
        item['relational_op'] = st.selectbox(label="Relational Op", options=relationals, key=next(widget_id))
    with cols[3]:
        item['value'] = st.text_input("Value", "", key=next(widget_id))
    with cols[4]:
        item['quanifier'] = st.selectbox(label="Quantifier", options=quantifiers, key=next(widget_id))
    with cols[5]:
        item['categorical'] = st.selectbox(label="Categoricals", options=categoricals, key=next(widget_id))
    with cols[6]:
        if next_exists:
            item['logical_op'] = sac.segmented(
                items=[
                    sac.SegmentedItem(label='AND'),
                    sac.SegmentedItem(label='OR'),
                ], label="&nbsp;", align='left', index=['AND','OR'].index(item["logical_op"]), key=next(widget_id))
        else:
            sac.segmented(items=[], label="&nbsp;", align='left', key=next(widget_id))
    with cols[7]:
        sac.buttons([sac.ButtonsItem(icon='trash')], label="&nbsp;", key=next(widget_id))

def update_props():
    st.session_state['temp'] = 'Dataraft'
            
def rule(this_condition=None):
    c1, c2, c3 = st.columns([0.4,0.4,3])
    with c1:
        add_condition = st.button('Add rule', key=next(widget_id))
    with c2:
        add_group = st.button('Add group', key=next(widget_id))

    if add_group:
        conditions.append([{"logical_op": "AND"}])

    if add_condition:
        this_condition.append({"logical_op": "AND"})
        #conditions.append({"logical_op": "AND"})
        st.session_state['conditions'] = conditions

def loopover(cond):
    for i, condition_item in enumerate(cond):
        if type(condition_item) == type({}):
            condition(condition_item, i, next_exists=i<len(cond)-1)
        else:
            with st.container(border=True):
                rule(this_condition=condition_item)
                loopover(condition_item)

tab1, tab2 = st.tabs(["Rules", "Data"])

with tab1:
    with st.container(border=True):
        rule(this_condition=conditions)
        loopover(conditions)
            
with tab2:
    nums = []
    cats = []
    t1, t2 = st.columns(2)
    with t1:
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            nums = [col for i,col in enumerate(df.columns) if df.dtypes[i] in [np.float64, np.int64]]
            cats = [col for i,col in enumerate(df.columns) if df.dtypes[i] in [np.object]]
            st.dataframe(df)
            st.session_state['numericals'] = nums
            st.session_state['categoricals'] = cats
            st.rerun()
    with t2:
        pass
