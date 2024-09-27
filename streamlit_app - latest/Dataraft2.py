
import streamlit as st
import streamlit.components.v1 as components
import hydralit_components as hc
import json
from streamlit_extras.stylable_container import stylable_container
import streamlit_antd_components as sac
import pandas as pd
import util
from datatable import dt, f
from st_aggrid import AgGrid, GridOptionsBuilder
import numpy as np
from pytexit import py2tex
import random
from hhome import navbar
from Jay_duckdb2 import csv_to_jay_to_duckdb
import streamlit.components.v1 as components
import hydralit_components as hc
import json
import time
from streamlit_extras.stylable_container import stylable_container
import streamlit_antd_components as sac
import graphviz
import pandas as pd
from st_login_form import login_form
import util
import os
import glob
from st_aggrid import AgGrid, GridOptionsBuilder
import tasks
from Mergetojayandduckdb import merge_csv_to_jay_to_duckdb
from hhome import navbar
from fixedContainer import st_fixed_container

try:
    st.set_page_config(layout="wide",initial_sidebar_state='collapsed',)
except Exception:
    st.write('')
navbar()
st.markdown("""
        <style>

            .eczjsme9 {
                padding-top: 3rem
            }  

        .stTabs [data-baseweb="tab-list"] {
        display: flex;
        gap: 1px;
              
    }

        .stTabs [data-baseweb="tab"] {
            height: 30px;
           
           
            white-space: normal;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left:100px;
            padding-right:100px;
            font-weight: bold;
        }
        .st-emotion-cache-6qob1r.eczjsme3 {
            background-color:#F0F2F6;
        }

.stTabs [aria-selected="true"] {
    background-color: #003366;
    color: #FFFFFF;
}

.stTabs [aria-selected="false"] {
    background-color: #005577;
    color: #FFFFFF;
}

.stTabs [aria-selected="false"]:hover {
    background-color: #003366;
}

.stTabs [aria-selected="true"]:hover {
    background-color: #003366;
}
            
button[id^="tabs-bui"]{
    background-color: #007bff;
    color: #ffffff;
    padding: 10px 20px;
    border: none;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s ease;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    
}


button[id^="tabs-bui"][aria-selected="true"]{
    background-color: #0056b3;
}

button[id^="tabs-bui"]:hover{
    background-color: #0056b3;
}
span.st-emotion-cache-10trblm.e1nzilvr1 {
    padding-top: 20px;
}
            

      
    </style>""", unsafe_allow_html=True)
@st.experimental_dialog("Help")
def ibutton(text):
    st.write(text)


widget_id = (id for id in range(1, 10000))
session = util.check_session()


def home():
        
        user = util.get_one_item(collection='users', username=st.session_state.username)
        organization = util.get_one_item(collection='organization', organization=user['organization'])
        datasets = util.get_if_array_contains(collection='datasets', values=user['groups'], owner=user['username'])
        user_datasets = [item['name'] for item in datasets['data']] 
        
        tab1,tab3,tab4,tab5 = st.tabs(["Workspaces","Groups","Configure Data","Rule Engine"])
        
        
        with tab1:
                with st.container(border=True):
                    l1,l2=st.columns([10,1])
                    with l1:
                        tab_id = sac.tabs([sac.TabsItem(label='Create Workspace'),sac.TabsItem(label='Modify Workspace')], align='left',color='blue')
                    with l2:
                        i=st.button(label=":information_source:")
                        if i:
                            ibutton("""A Workspace acts as a folder into which data can be added. 
                                   \nCreate new Workspace(s) or upload data to Workspace(s) under 'Create Workspace'.
                                    \nAdd groups to Workspace(s) which makes the data accessible to the users in that group.
                                   \nAdd properties, i.e, to Workspace(s). Example:
                                    \n                                             Property     Value 
    field_test   72
                                    \nPick a Workspace and load data files into the Workspace and properties to the individual files. Example:
                                     \n                                             Property     Value 
    Battery_lab_test     1200
                                  \nModify existing Workspace(s) under 'Modify Workspace'.""")
                    c1,c2=st.columns([1,1])
                    if tab_id=='Create Workspace':
                      with c1:
                       with st.container(border=True):
                        selected_dataset=None

                        dataset_name = st.text_input('##### :orange[Workspace Name]',placeholder="Enter Workspace Name")
                        with st.form("dataset",border=False):        
                                group_list = util.get_list(collection='users', projection={'groups': 1}, username=st.session_state.username)
                                groups = group_list['data'][0]['groups']
                                if selected_dataset is None:
                                    st.markdown("##### :orange[Assign groups to workspace]")
                                    # st.markdown("Existing Groups&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Selected Groups")

                                    selected_groups = sac.transfer(items=groups,width=250,align='left',titles=['Existing Group(s)','Selected Group(s)'],color='violet')
                                    pdf = pd.DataFrame([{"Property": "", "Value": ""} for i in range(5)])
                                else:
                                    pass
                                with st.expander("Add Workspace properties"):
                                    properties = st.data_editor(pdf, hide_index=True, width=350)
                                            
                                dataset_submitted = st.form_submit_button("Submit")
                                if dataset_submitted:
                                    given_properties = [(pair[0], pair[1]) for pair in zip(list(properties.Property), list(properties.Value)) if pair[0] != '' and pair[1] != '']
                                    if selected_dataset is None:
                                        os.mkdir(f'{organization[r"dataPath"]}/{dataset_name}')
                                        result = util.insert_one(collection='datasets', doc={'name': dataset_name, 'username':st.session_state.username, 'organization':user['organization'], 'groups':selected_groups, 'properties': given_properties})
                                        if not result['status']:
                                            st.error('This workspace name already exists')
                                        else:
                                            st.success('Workspace created')
                                            time.sleep(2)
                                            st.switch_page('Dataraft2.py')
                                    else:
                                        util.update_one(collection='datasets', key={'name': selected_dataset}, doc={'$set': {'groups':selected_groups, 'properties': given_properties}})
                      with c2:
                        with st.container(border=True):

                            selected_dataset = st.selectbox("##### :orange[Pick a workspace to load Data]", user_datasets)
                            if selected_dataset:
                                list_of_files = glob.glob(f'{organization["dataPath"]}/{selected_dataset}/*.csv')
                                if len(list_of_files) == 0:
                                    st.warning('Currently there are no uploaded data files in this workspace')
                                else:
                                    p1, p2 = st.columns([1,2])
                                    with p1:
                                        df = pd.DataFrame([[os.path.basename(item),False] for item in list_of_files], columns=['Data File', 'Delete'])
                                        builder = GridOptionsBuilder.from_dataframe(df)
                                        builder.configure_selection("Data File", use_checkbox=True)
                                        go = builder.build()

                                        selected_files = AgGrid(df, gridOptions=go)
                                        delete_submitted = st.button("Delete")
                                        if delete_submitted:
                                            for deleted_file in selected_files.selected_rows:
                                                os.remove(f'{organization["dataPath"]}/{selected_dataset}/{deleted_file["Data File"]}')
                                                st.rerun()
                                    with p2:
                                        if selected_files['selected_rows']:
                                            full_path = f'{organization["dataPath"]}/{selected_dataset}/{selected_files["selected_rows"][0]["Data File"]}'
                                            current_properties = util.get_one_item(collection='fileproperties', filename=full_path)
                                            current_properties['properties'].extend([['',''] for i in range(5-len(current_properties['properties']))]) 
                                            pdf = pd.DataFrame(columns=["Property", "Value"], data=current_properties['properties'])
                                            updated_properties = st.data_editor(pdf, width=350, key=next(widget_id))

                                            property_update_submitted = st.button("Update Properties")
                                            if property_update_submitted:
                                                this_file_properties = [(pair[0], pair[1]) for pair in zip(list(updated_properties.Property), list(updated_properties.Value)) if pair[0] != '' and pair[1] != '']
                                                util.update_one(collection='fileproperties', key={'filename': full_path}, doc={'$set': {'properties': this_file_properties}}, upsert=True)
                                                st.rerun()
    
                            uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True, key=next(widget_id),disabled=selected_dataset is None)

                            file_count = len(uploaded_files)
                            i = 0
                            file_properties = {}
                            while i < file_count:
                                f1, f2 = st.columns([1,1])
                                with f1:
                                    st.write(uploaded_files[i].name)
                                    pdf = pd.DataFrame([{"Property": "", "Value": ""} for i in range(5)])
                                    file_properties[uploaded_files[i].name] = st.data_editor(pdf, width=350, key=next(widget_id))
                                    i += 1
                                if i < file_count:
                                    with f2:
                                        st.write(uploaded_files[i].name)
                                        pdf = pd.DataFrame([{"Property": "", "Value": ""} for i in range(5)])
                                        file_properties[uploaded_files[i].name] = st.data_editor(pdf, width=350, key=next(widget_id))
                                        i += 1
                        
                            load_submitted = st.button("Submit",disabled = (len(uploaded_files)==0))
                            try:
                                if load_submitted:
                                    for uploaded_file in uploaded_files:
                                        udf = pd.read_csv(uploaded_file, encoding = "ISO-8859-1")
                                        full_path = f'{organization["dataPath"]}/{selected_dataset}/{uploaded_file.name}'
                                        
                                        udf.to_csv(f'{organization["dataPath"]}/{selected_dataset}/{uploaded_file.name}')
                                        
                                        this_file_properties = [(pair[0], pair[1]) for pair in zip(list(file_properties[uploaded_file.name].Property), list(file_properties[uploaded_file.name].Value)) if pair[0] != '' and pair[1] != '']
                                        
                                        util.update_one(collection='fileproperties', key={'filename': full_path}, doc={'$set': {'properties': this_file_properties}}, upsert=True)
                                    
                                        merge_csv_to_jay_to_duckdb.delay(f'{organization["dataPath"]}/{selected_dataset}')
                                    
                                    if len(list_of_files)==0:
                                            st.success('Workspace successfully uploaded')
                            
                                    if len(list_of_files)>0:
                                            st.success('Workspace updated successfully')
                            except OSError as o:
                                st.error("The workspace folder path is missing. Please check and try again!")
                            except ValueError as v:
                                st.error("Wrong type/combinations of workspaces uploaded. Please try again!")
            
                    elif tab_id=="Modify Workspace":

                        c1,c2=st.columns([1,1])
                        with c1:
                            selected_dataset = st.selectbox('##### :orange[Pick Workspace]', user_datasets, index=None, placeholder="Choose a Workspace")
                            if selected_dataset:
                                selected_dataset_details = util.get_one_item(collection='datasets', name=selected_dataset, username=user['username'])
                                # selected_dataset_details = util.get_if_array_contains(collection='datasets', name=selected_dataset, username=user['username'])

                            with st.form("chooseDataset",border=False):
                                group_list = util.get_list(collection='users', projection={'groups': 1})
                                groups = group_list['data'][0]['groups']
                                 
                                if selected_dataset is None:
                                    st.warning('Workspace not selected!')
                                    selected_groups = sac.transfer(items=groups,titles=['Existing Group(s)','Selected Group(s)'],color='violet',width=250)
                                    pdf = pd.DataFrame([{"Property": "", "Value": ""} for i in range(5)]) 

                                else:
                                    index = [groups.index(item) for item in selected_dataset_details['groups']]
                                    st.markdown("##### :orange[Assign groups to workspace]")
                                    # st.markdown("Existing Groups&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Selected Groups")
                                    selected_groups = sac.transfer(items=groups, index=index,titles=['Existing Group(s)','Selected Group(s)'],color='violet',width=250)
                                    if 'properties' not in selected_dataset_details:
                                        pdf = pd.DataFrame([{"Property": "", "Value": ""} for i in range(5)])
                                    else:
                                        properties_data = selected_dataset_details['properties']
                                        properties_data.extend([['',''] for i in range(5-len(properties_data))]) 
                                        pdf = pd.DataFrame(columns=["Property", "Value"], data=properties_data)
                                with st.expander("Add Workspace properties here"):
                                    properties = st.data_editor(pdf, hide_index=True, width=350)
                                            
                                dataset_submitted = st.form_submit_button("Submit")
                                
                                if dataset_submitted:

                                    given_properties = [(pair[0], pair[1]) for pair in zip(list(properties.Property), list(properties.Value)) if pair[0] != '' and pair[1] != '']
                                
                                    if selected_dataset is None:
                                        os.mkdir(f'{organization[r"dataPath"]}/{dataset_name}')
                                        result = util.insert_one(collection='datasets', doc={'name': dataset_name, 'username':st.session_state.username, 'organization':user['organization'], 'groups':selected_groups, 'properties': given_properties})
                                        if not result['status']:
                                            st.error('This workspace name already exists')
                                        else:
                                            st.success('Workspace created')
                                    else:
                                        util.update_one(collection='datasets', key={'name': selected_dataset}, doc={'$set': {'groups':selected_groups, 'properties': given_properties}})

        with tab3:
            col1,col2=st.columns([1,1])
            with col1:
                    with st.container(border=True):
                        l1,l2=st.columns([10,1])
                        with l1:
                            tab_id = sac.tabs([sac.TabsItem(label='Create Group'),sac.TabsItem(label='Modify Group')], align='left',color='blue')
                        with l2:
                            i=st.button(label=":information_source:", key='Group')
                            if i:
                                ibutton("""Create Group(s) and users under 'Create Group'. 
                                        \nModify existing Group(s) under 'Modify Group'.""" )
                        if tab_id=="Create Group":
                            group_name = st.text_input('Group name', value='')
                            with st.form("group"):
                                
                                
                                st.markdown("##### :orange[Assign users to group]")
                                
                                # st.markdown("Existing Users&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Selected Users")
                                user_list = util.get_list(collection='users', projection={'username': 1, 'firstname': 1, 'lastname': 1})
                                users = [f'{item["username"]}-{item["firstname"]} {item["lastname"]}' for item in user_list['data']]
                                
                                
                                selected_users = sac.transfer(items=users,titles=['Existing User(s)','Selected User(s)'],width=250,color='violet')
                                        
                                group_submitted = st.form_submit_button("Submit")

                                if group_submitted:
                                        if len(group_name.strip())==0:
                                            st.error("Group name is Missing!")
                                        if '-' in group_name:
                                            st.error("Name cannot have '-'")

                                        if group_name in user['groups']:
                                            st.error('Group name already exists')
                                            exit()
                                        else:
                                            result = util.insert_one(collection='groups', doc={'groupName': group_name, 'username':st.session_state.username, 'members':selected_users})
                                        try:
                                            for member in selected_users:
                                                util.update_one(collection='users', key={'username': member.split('-')[0]}, doc={'$push': {'groups': group_name}})
                                            st.success("Group created successfully!")
                                        except TypeError as v:
                                            st.error("Group without users cannot be created. Please try again!")

                                else:
                                    util.update_one(collection='groups', key={'groupName': group_name}, doc={'$set': {'members':selected_users}})
                        if tab_id=="Modify Group":
                            
                                
                                selected_group = st.selectbox("Pick a Group", user['groups'], index=None)

                                if selected_group:
                                    selected_group_details = util.get_one_item(collection='groups', groupName=selected_group, username=user['username'])
                                with st.form("groups"):
                                    user_list = util.get_list(collection='users', projection={'username': 1, 'firstname': 1, 'lastname': 1})
                                    users = [f'{item["username"]}-{item["firstname"]} {item["lastname"]}' for item in user_list['data']]
                                    if selected_group is None:
                                        st.warning('Group not selected')
                                    else:
                                        try:
                                            index = [users.index(item) for item in selected_group_details['members']]
                                            st.markdown("##### :orange[Assign users to group]")
                                            # st.markdown("Existing Users&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Selected Users")
                                            selected_users = sac.transfer(items=users, index=index, titles=['Existing User(s)','Selected User(s)'],width=250,color='violet')
                                        except TypeError as t:
                                            st.error("The group is either corrupted or has been deleted from the collection 'groups'. Please check and try again")
                                    group_submitted = st.form_submit_button("Submit")

                                    if group_submitted:
                                        if selected_group is None:
                                            if len(group_name.strip())==0:
                                                st.error("Group name is Missing!")
                                            if '-' in group_name:
                                                st.error("Name cannot have '-'")
                                            else:
                                                result = util.insert_one(collection='groups', doc={'groupName': group_name, 'username':st.session_state.username, 'members':selected_users})
                                                for member in selected_users:
                                                    util.update_one(collection='users', key={'username': member.split('-')[0]}, doc={'$push': {'groups': group_name}})

                                        else:
                                            
                                            util.update_one(collection='groups', key={'groupName': group_name}, doc={'$set': {'members':selected_users}})
                                            st.success("Group Updated!")  
        with tab4:
            columns = []

            domains = ['Electrical', 'Human Resources']
            subdomains = ['Battery']

            tab_id = ''
            def get_sample_data(data_path):
                data_table = dt.Frame(data_path)
                row_count = data_table.shape[0]
                if row_count < 25:
                    df = data_table.to_pandas()
                else:
                    start = random.randint(0, row_count-25)
                    df = data_table[start:start+24, :].to_pandas()
                return df
                
            def configure_data():
                st.subheader('Configure your data')
                user = util.get_user(st.session_state.username)
                organization = util.get_one_item(collection='organization', organization=user['organization'])
                datasets = util.get_if_array_contains(collection='datasets', values=user['groups'], owner=user['username'])
                user_datasets = [item['name'] for item in datasets['data']] 

                columns = []
                c1, c2 = st.columns([1,1])
                with c1:
                    selected_dataset = st.selectbox(
                        "Pick a Workspace", user_datasets, index=None, key=next(widget_id))
                
                if selected_dataset is not None:
                    csv_path=f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv'
                    try:
                        df = pd.read_csv(csv_path)

                        if df.isnull().any().any():
                            st.markdown("##### :orange[The data configuration cannot proceed due to the following problems:]")
                            with st.container(border=True,height=150):
                                n1,n2=st.columns([6,1])
                                with n2:
                                    if st.button("Skip Data Cleaning",type='primary',key='first'):
                                        with n1:
                                            st.warning("Data configuration cannot proceed without cleaning data")
                                
                                    else:
                                        with n1:
                                            null_columns = df.columns[df.isnull().any()]

                                            for column in null_columns:
                                                if df[column].dtype == float:
                                                    st.markdown(f"*Numeric column: {column} has NULL values*")
                                                if df[column].dtype == "object":
                                                    st.markdown(f"*Categorical column: {column} has NULL values*")
                                                if df[column].dtype == "datetime64[ns]":
                                                    st.markdown(f"*Date type column: {column} has NULL values*")

                                                if df[column].dtype == float:
                                                    float_button = st.button(f"Replace with Mean value?", key=f"numeric_{column}")
                                                    
                                                    if float_button:
                                                        mean_value = df[column].mean()
                                                        df[column].fillna(mean_value, inplace=True)
                                                        st.success(f"Column(s): {column} has/have been replaced with mean value.")
                                                elif df[column].dtype == 'object':
                                                    string_button = st.button(f"Replace with most repeated String value?", key=f"string_{column}")
                                                    if string_button:
                                                        mode_value = df[column].mode()[0] if len(df[column].mode()) > 0 else ''
                                                        df[column].fillna(mode_value, inplace=True)
                                                        st.success(f"Column(s): {column} has/have been replaced with the most repeated string value.")
                                                elif df[column].dtype == 'datetime64[ns]':
                                                    date_button = st.button(f"Replace it with the earliest date value?", key=f"date_{column}")
                                                    if date_button:
                                                        try:
                                                            pd.to_datetime(df[column])
                                                            earliest_date = df[column].min()
                                                            df[column].fillna(earliest_date, inplace=True)
                                                            st.success(f"Column(s): {column} has/have been replaced with the earliest date value.")
                                                        except ValueError:
                                                            st.error(f"Column {column} is not in a valid datetime format.")
                                        df.to_csv(csv_path, index=False)
                                        csv_to_jay_to_duckdb.delay(f'{organization["dataPath"]}/{selected_dataset}')
                

                                null_values = df.isnull()
                                null_rows_indices = np.where(null_values.any(axis=1))[0]
                                
                            if null_rows_indices.size > 0:
                                st.write("*The following are sample null values in the dataset:*")
                                all_null_rows = df.iloc[null_rows_indices]
                                st.write(all_null_rows)
                
                        else:
                            st.markdown("###### :green[The Data is clean, you can now configure your data. Click on the button below and the sidebar to configure data.]")
                            try:
                                pdf = get_sample_data(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                            except Exception as e:
                                st.error("The worspace was not found. Please try again!")
                        
                            if st.button("Sample Data", type="secondary"):
                                pdf = get_sample_data(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                            try:
                                pdf = get_sample_data(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                            except Exception as e:
                                st.write(e)

                            st.dataframe(pdf)
                            columns = pdf.columns.values.tolist()
                            pdf_column_types = pdf.dtypes.tolist()
                            numeric_columns = [pair[0] for pair in zip(columns, pdf_column_types) if pair[1] in [np.float64]] 
                    except FileNotFoundError as f:
                        st.error("The merged workspace was not foud. Please try again")   
                with st.sidebar:
                    if len(columns) > 0:
                        st.markdown("###### :orange[Configure your data here]")
                        with st.container(border=True):
                            
                            target_var = st.selectbox("Identify Targets", numeric_columns, index=None, placeholder="Choose a variable")
                            cr1, cr2 = st.columns([2,1])
                            with cr1:
                                success_criteria = st.text_input(label='Success criteria', disabled=target_var==None)
                            with cr2:
                                st.markdown("""<div style='padding-top:1.9rem'/>""", unsafe_allow_html=True)
                                create_target = st.button('Create', disabled=target_var==None)
                                if create_target:
                                    util.update_one(collection='datasets', key={'name': selected_dataset}, doc={'$push': {'targets':{'name': target_var, 'successCriteria':success_criteria}}})
                                    df = dt.Frame(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                                    expression = f'f.{target_var} {success_criteria}'
                                    exec(f'df["response{target_var}"] = {expression}')    
                                    df.to_csv(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                                    st.rerun()
                            
                        with st.container(border=True):
                            column_type = ['Formula', 'Norm Dist.', 'Constant']
                            add_option = st.selectbox("Add Column", column_type, index=None, placeholder="Choose a type")
                            variable_name = st.text_input(label='Name')
                            if add_option == 'Formula':
                                variable_name = st.text_area(label='Formula')
                                with st.popover("Variables"):
                                    for col in columns:
                                        st.code(col)
                            else:    
                                variable_value = st.text_input(label='Value')
                                
                            add_submitted = st.button("Add")
                            if add_submitted:
                                df = dt.Frame(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                                if add_option == 'Constant':
                                    df[variable_name] =  variable_value
                                elif add_option == 'Norm Dist.':
                                    mu, sigma = variable_value.split(',')
                                    df[variable_name] =  np.random.normal(float(mu), float(sigma), df.shape[0])
                                elif add_option == 'Formula':
                                    expression = variable_value
                                    for col in columns:
                                        expression = expression.replace(col, f'f.{col}')
                                    st.write(f'df["{variable_name}"] = {expression}')    
                                    exec(f'df["{variable_name}"] = {expression}')    
                                    st.latex(py2tex(variable_value).replace('$$', '', 10))
                                df.to_csv(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                                csv_to_jay_to_duckdb.delay(f'{organization["dataPath"]}/{selected_dataset}')
                                st.rerun()

                        with st.form('delete column'):
                            delete_option = st.selectbox("Delete Column", columns, index=None, placeholder="Select a column")
                            
                            delete_submitted = st.form_submit_button("Delete")
                            if delete_submitted:
                                util.update_one(collection='datasets', key={'name': selected_dataset}, doc={'$pull': {'targets':{'name': delete_option}}})
                                df = dt.Frame(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                                del df[:, delete_option]
                                df.to_csv(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv')
                                csv_to_jay_to_duckdb.delay(f'{organization["dataPath"]}/{selected_dataset}')
                                st.rerun()

            def nomenclature():
                user = util.get_user(st.session_state.username)
                organization = util.get_one_item(collection='organization', organization=user['organization'])
                datasets = util.get_if_array_contains(collection='datasets', values=user['groups'], owner=user['username'])
                user_datasets = [item['name'] for item in datasets['data']] 
                h1, h2 = st.columns([2,1])
                with h1:
                    st.subheader('Name Mapper')
                    
                c1, c2 = st.columns([1,1])
                with st.sidebar:
                    if tab_id == 'Nomenclature':
                        st.markdown("##### :orange[Select a workspace]")
                        selected_dataset = st.selectbox(
                            "", user_datasets, index=None, key=next(widget_id))
                        d1, d2 = st.columns([1,1])
                        with d1:
                            selected_domain = st.selectbox(
                                "Pick a Domain", domains, index=None, key=next(widget_id))
                        with d2:
                            selected_subdomain = st.selectbox(
                                "Pick a Subdomain", subdomains, index=None, key=next(widget_id))
                        
                        if selected_domain is not None:
                            attr_condition = {'domain': selected_domain}
                            if selected_subdomain is not None:
                                attr_condition = {'subdomain': selected_subdomain}
                                
                            terms_result = util.get_list(collection='terms', attribute=attr_condition, projection={'term': 1})
                            domain_terms = [item['term'] for item in terms_result['data']] 

                with h2:
                    a1, a2 = st.columns([1,1])
                    with a1:
                        if selected_dataset is not None:
                            update_submitted = st.button('Update')
                    with a2:
                        try:
                            if domain_terms is not None:
                                with st.popover("Variables"):
                                    for term in domain_terms:
                                        st.code(term, language='log')
                        except:
                            pass
                if selected_dataset is None:
                    st.markdown("#### :red[Choose a workspace in the sidebar to map variables]")
                if selected_dataset is not None:
                    try:
                        header = dt.Frame(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.csv').head(0).to_pandas()
                        ndf = pd.DataFrame(columns=['Data Variables'], data=header.columns.tolist())
                        ndf['Mapped'] = ''
                        
                        mapped_terms = util.get_one_item(collection='datasets', name=selected_dataset, organization=user['organization'], projection={'termMap':[]})
                        mapped_df = pd.DataFrame(columns=['Data Variables', 'Mapped'], data=mapped_terms['termMap'])
                        
                        ndf = ndf.merge(mapped_df, on=['Data Variables'], how='left')
                        ndf.rename(columns={'Mapped_y': 'Mapped'}, inplace=True)
                        ndf.drop(['Mapped_x'], axis=1, inplace=True)
                        mapper = st.data_editor(ndf, use_container_width=True)
                        if update_submitted:
                            mapped = [(pair[0], pair[1]) for pair in zip(list(mapper['Data Variables']), list(mapper.Mapped)) if pair[0] != '' and pair[1] != '']                    
                            util.update_one(collection='datasets', key={'name': selected_dataset}, doc={'$set': {'termMap':mapped}})
                            st.success("Term mapping updated successfully")
                    except ValueError as v:
                        st.error("The merged workspace was not foud. Please try again")          
            if session is None and 'authenticated' not in st.session_state:
                st.markdown("""
                <style>
                    [data-testid="collapsedControl"] {
                        display: none
                    }
                </style>
                """,
                    unsafe_allow_html=True,
                )
                
                util.login()
            else:

                st.markdown('#')
                tab_id = sac.tabs([
                    sac.TabsItem(label='Configure'),
                    sac.TabsItem(label='Nomenclature')
                ], align='left',color='blue')
                
                if tab_id == 'Configure':
                    try:
                        configure_data()
                    except PermissionError as p:
                        st.error(p)
                        st.error("The excel sheet is open, please close it")

                if tab_id == 'Nomenclature':
                    nomenclature()

loginCount=0          

if (session is None and 'authenticated' not in st.session_state) or ('authenticated' in st.session_state and not st.session_state.authenticated):
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
   
    util.login()
  
    
else:
    try:
        home()
    except FileExistsError as e:
        st.error("A workspace with the same name already exists in the folder. Please try again!")  