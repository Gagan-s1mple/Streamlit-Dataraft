
import streamlit as st
import pandas as pd
import duckdb
import streamlit.components.v1 as components
import hydralit_components as hc
import streamlit_antd_components as sac
from itertools import combinations
from streamlit_extras.stylable_container import stylable_container
import matplotlib.pyplot as plt
import numpy as np
import plotly.figure_factory as ff
import seaborn as sns
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import splrep, BSpline
import altair as alt
import util
import hhome
st.set_page_config(layout="wide",initial_sidebar_state='expanded',)
hhome.navbar()
@st.experimental_dialog("Help")
def ibutton(text):
    st.write(text)
st.markdown("""
        <style>

        .st-emotion-cache-6qob1r.eczjsme3 {
            background-color:#F0F2F6;
        }
            .eczjsme9 {
                padding-top: 0rem
            }
               .block-container {
                    padding-top: 1.75rem;
                }
                
                .element-container {
                    padding-top: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)



b1,b2 = st.columns([10,1])
with b2:
    session = util.check_session()

widget_id = (id for id in range(1, 100_00))
def project():
    protabs = sac.tabs([
            sac.TabsItem(label='Link Datasets'),
            sac.TabsItem(label='Start Analysis')
        ], align='left',color='blue')
    
    user = util.get_user(st.session_state.username)
    organization = util.get_one_item(collection='organization', organization=user['organization'])
    datasets = util.get_if_array_contains(collection='datasets', values=user['groups'], owner=user['username'])
    user_datasets = [item['name'] for item in datasets['data']] 
    projects = util.get_list(collection='projects', username=user['username'])
    user_projects = [item['projectName'] for item in projects['data']]
    dataset_schema = {}
    if protabs=='Link Datasets':
        for dataset in user_datasets:
            try:
                ducon = duckdb.connect(database=f'{organization["dataPath"]}/{dataset}/{dataset}.duckdb', read_only=True)
                schema = ducon.sql(f'describe {dataset}').df()
                dataset_schema[dataset] = schema['column_name'].values.tolist()
            except duckdb.CatalogException as c:
                st.error(c)
                st.error("The duckdb file of the above workspace has been removed/doesn't exist. Please try again!")
        h1, h2 = st.columns([2.8,2])

            
        if len(user_projects) == 0:
            st.warning('Currently, you have not projects set up')
            st.page_link("Dataraft2.py", label="Please click here to set up your projects")
        else:
            with st.sidebar:
                st.markdown("### :blue[Choose a Project]")
                selected_project = st.selectbox('', user_projects, label_visibility="hidden", index=None)
                with h1:
                    if selected_project is not None:
                        st.write(
                                f'<span style="font-size: 30px; font-weight: bold;">{selected_project}</span>',
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown("### :orange[Project]")
                        st.markdown("#### :red[Please choose a project on the sidebar to continue]")
                with h2:
                    save_submitted = st.button('Save')
                
        try:
            if selected_project is not None:
                c1, c2 = st.columns([1,1])
                with c1:
                    project_details = [item for item in projects['data'] if item['projectName'] == selected_project][0]
                    if 'datasetLinkSchema' in project_details:
                        dataset_keys = project_details['datasetLinkSchema']
                    else:
                        dataset_keys = {}
                    if 'datasets' in project_details:
                        if len(project_details['datasets']) > 1:
                            pairs = list(combinations(project_details['datasets'], 2))
                            for pair in pairs:
                                with st.container(border=True):
                                    st.subheader(f'{pair[0]} → {pair[1]}')
                                    s1, s2 = st.columns([1,1])
                                    if f'{pair[0]}-{pair[1]}' not in dataset_keys:
                                        dataset_keys[f'{pair[0]}-{pair[1]}'] = ['','']
                                    with s1:
                                        try:
                                            dataset_keys[f'{pair[0]}-{pair[1]}'][0] = st.selectbox(pair[0], dataset_schema[pair[0]], index=dataset_schema[pair[0]].index(dataset_keys[f'{pair[0]}-{pair[1]}'][0]), key=next(widget_id))
                                        except ValueError as e:
                                            dataset_keys[f'{pair[0]}-{pair[1]}'][0] = st.selectbox(pair[0], dataset_schema[pair[0]],key=next(widget_id))
                                        except KeyError as k:
                                            st.error("The table couldn't be created since the duckdb file doesn't exist")
                                    with s2:
                                        try:
                                            dataset_keys[f'{pair[0]}-{pair[1]}'][1] = st.selectbox(pair[1], dataset_schema[pair[1]], index=dataset_schema[pair[1]].index(dataset_keys[f'{pair[0]}-{pair[1]}'][1]), key=next(widget_id))
                                        except ValueError as e:
                                            dataset_keys[f'{pair[0]}-{pair[1]}'][1] = st.selectbox(pair[1], dataset_schema[pair[1]],key=next(widget_id))
                                        except KeyError as k:
                                            st.error("The table couldn't be created since the duckdb file doesn't exist")
                        else:
                            st.warning('There are no workspaces/ only one dataset assigned to the project')            
                    else:
                        st.warning('Selected project does not have any assigned workspaces')            
                with c2:
                    if len(dataset_keys.keys()) > 0:
                        digraph = "digraph { rankdir=\"TB\" "
                        for key in dataset_keys:
                            parts = key.split('-')
                            digraph += f'"{parts[0]}"'
                            digraph += " -> "
                            digraph += f'"{parts[1]}" [label="{dataset_keys[key][0]}"] '
                            
                            digraph += f'"{parts[1]}"'
                            digraph += " -> "
                            digraph += f'"{parts[0]}" [label="{dataset_keys[key][1]}"] '
                            
                        digraph += "}"

                    st.graphviz_chart(digraph)
        except UnboundLocalError as e:
            st.write("")
        if save_submitted:
            util.update_one(collection='projects', key={'projectName': selected_project, 'username': user['username']}, doc={'$set': {'datasetLinkSchema':dataset_keys}})

    if protabs == 'Start Analysis':
        c1,c2=st.columns([1,1])
        with c1:
                with st.container(border=True):
                    c1,c2=st.columns([10,1])
                    with c1:
                        tab_id = sac.tabs([
                        sac.TabsItem(label='Create Project'),
                        sac.TabsItem(label='Modify Project')
                        ], align='left',color='blue')
                    with c2:
                        p=st.button(label=":information_source:", key='project')
                        if p:
                            ibutton("""Create new Project(s) under 'Create Project' and  add Workspace(s) to Project(s). 
                                    \nModify existing Project(s) under 'Modify Project'.""")


                    if tab_id == "Create Project":
                            selected_project=None
                            project_name = st.text_input('Project name', placeholder='Enter project name')

                            with st.form("createproject"):
                                if selected_project is None:
                                    st.markdown("##### :orange[Assign workspaces to project]")
                                    
                                    # st.markdown("Existing Datasets&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Selected Datasets")
                                    selected_datasets = sac.transfer(items=user_datasets, titles=['Existing Workspace(s)','Selected Workspace(s)'],width=250,color='violet')

                                else:
                                    project_name = st.text_input('Project name', value=selected_project_details['projectName'])
                                    index = [user_datasets.index(item) for item in selected_project_details['datasets']]
                                    selected_datasets = sac.transfer(items=user_datasets, index=index, titles=['Existing Workspace(s)','Selected Workspace(s)'],width=250,color='violet')
                                                

                                        
                                project_submitted = st.form_submit_button("Submit")
                                if project_submitted:
                                    if selected_project is None:
                                        result = util.insert_one(collection='projects', doc={'projectName': project_name, 'username':st.session_state.username, 'datasets':selected_datasets})
                                        
                                        if not result['status']:
                                            st.error('This project name already exists')
                                        else:
                                            util.update_one(collection='users', key={'username': st.session_state.username}, doc={'$push': {'projectsOwned': project_name}})
                                            st.success('Project created successfully')
                                    else:
                                        util.update_one(collection='projects', key={'projectName': project_name}, doc={'$set': {'datasets':selected_datasets}})

                    if tab_id == "Modify Project":
                            
                            with st.container(border=False):
                                selected_project = st.selectbox("Pick a Project", user['projectsOwned'] + user['projectsSharedWith'], index=None)
                                if selected_project:
                                    selected_project_details = util.get_one_item(collection='projects', projectName=selected_project, username=user['username'])
                                with st.form("project", border=True):
                                    
                                    if selected_project is None:
                                        st.warning('Project not selected!')
                                    else:
                                        try:
                                            project_name =selected_project_details['projectName']
                                            index = [user_datasets.index(item) for item in selected_project_details['datasets']]
                                            st.markdown("##### :orange[Assign workspaces to project]")
                                            # st.markdown("Existing Datasets&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Selected Datasets")
                                            selected_datasets = sac.transfer(items=user_datasets, index=index,titles=['Existing Workspace(s)','Selected Workspace(s)'],width=250,color='violet')
                                        except ValueError as v:
                                            st.error(v)
                                            st.error("The above workspace has been deleted from the database. Please check and try again!")
                                        except TypeError as t:
                                            st.error("The project has been removed from the 'projects' collection. Please check and try again!")
                                    project_submitted = st.form_submit_button("Submit")
                                    if project_submitted:
                                        if selected_project is None:
                                            result = util.insert_one(collection='projects', doc={'projectName': project_name, 'username':st.session_state.username, 'datasets':selected_datasets})
                                            if not result['status']:
                                                st.error('This project name already exists')
                                            else:
                                                util.update_one(collection='users', key={'username': st.session_state.username}, doc={'$push': {'projectsOwned': project_name}})
                                                st.success('Project created successfully')
                                        else:
                                            util.update_one(collection='projects', key={'projectName': project_name}, doc={'$set': {'datasets':selected_datasets}})               

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
    st.markdown("#")
    try:
        project()

    except UnboundLocalError as u:
        st.warning("You cannot proceed without setting up a project")
