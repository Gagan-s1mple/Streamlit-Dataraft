import streamlit as st
import util
import os
st.set_page_config(layout="wide",initial_sidebar_state='collapsed')


st.markdown(
   """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

def admin():
    st.header('Admin page')
    h1,h2=st.columns([1,1])
    with h1:
        h3,h4=st.columns([1,1])
        with st.form('Organization'):
            st.write('Create an organization')
            og_name=st.text_input('Organization Name')
            data_path=st.text_input('Organization Data Path')
            project_path=st.text_input('Organization Project Path')
            organization_submitted=st.form_submit_button('Submit')
            if organization_submitted:
                util.insert_one(collection='organization', doc={'organization':og_name,'dataPath':data_path,'name':og_name,'projectPath':project_path})
                st.success('Organization Created successfully')
    with h2:
        with st.form('User'):
            st.write('Create User')
            username=st.text_input('Enter Userame')
            firstname=st.text_input('Enter First Name')
            lastname=st.text_input('Enter Last Name')
            password=st.text_input('Enter Passsword', type='password')
            organization=st.text_input('Enter Organization')
            user_submitted=st.form_submit_button('Submit')
            if user_submitted:
                util.insert_one(collection='users',doc={'username':username,'firstname':firstname,'lastname':lastname,'password':util.get_hashed(password),'organization':organization,'groups':[username],'projectsOwned':[],'projectsSharedWith':[]})
                util.insert_one(collection='groups',doc={'groupName':username,'username':username,'members':[username + firstname]})
                st.success("User created successfully")
                os.mkdir(f"{data_path}/default_{username}")
                user = util.get_one_item(collection='users', username=username)
                result = util.insert_one(collection='datasets', doc={'name': f"default_{username}", 'username':username, 'organization':user['organization'], 'groups':username, 'properties': "This is a default workspace"})
admin()

