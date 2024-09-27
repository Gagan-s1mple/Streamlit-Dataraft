import pymongo
from pymongo import MongoClient
import hashlib
import urllib
import hmac
import streamlit as st
import extra_streamlit_components as stx
import redis
import time
from pymongo.errors import OperationFailure
import pyautogui

r = redis.Redis(host='localhost', port=6379, db=0)
cookie_manager = stx.CookieManager()

def connect_db():
    mongo_username = st.secrets.mongo.username
    mongo_password = st.secrets.mongo.password
    connection = f'mongodb://{urllib.parse.quote(mongo_username)}:{urllib.parse.quote(mongo_password)}@localhost:27017/dataraft'
    client=MongoClient(connection)
    db = client["dataraft"]
    return db

def get_user(uname):
    try:
        db = connect_db()
        user_db = db['users']
        result = user_db.find_one({'username': uname})

        return result

    except OperationFailure as e:
        st.error("MongoDB server authentication failed, please check you credentials")
        

def get_hashed(text):
    digest = hmac.new(bytes('data-in-knowledge-out', 'UTF-8'), msg=bytes(text, 'UTF-8'), digestmod=hashlib.sha256)
    signature = digest.hexdigest()
    return (signature)

def check_password(uname,pwd):
    try:
        db = connect_db()
        #with st.sidebar:
        user_db = db['users']
        result = user_db.find_one({'username': uname, 'password': get_hashed(pwd)}, {'_id' : 0, 'password': 0})
        return result
    except: 
        return -1
def get_one_item(collection=None, projection=None, **kwargs):
    try:
        db = connect_db()
        data_db = db[collection]
        if projection is None:
            projection = {}
        projection['_id'] = 0
        result = data_db.find_one(kwargs, projection)
        return result
    except OperationFailure as e:
        st.error("Unable to reach the previous session due to authentication failure. Please try again!")



def get_list(collection=None, attribute=None, username=None, projection=None, limit=None, skip=None):
    db = connect_db()
    data_db = db[collection]
    if projection is None:
        projection = {}
    projection['_id'] = 0

    if attribute is None:
        attribute = {}
        
    if username is not None:
        attribute['username'] = username

    if limit is None:
        limit = 0
    if skip is None:
        skip = 0    
    
    cursor = data_db.find(attribute, projection, limit=limit, skip=skip)
    result = list(cursor)
    
    if result is None:
        return {'status': False, 'data': None}
    else:
        return {'status': True, 'data': result}

def insert_one(collection=None, username=None, doc=None, duplicate_allowed=False):
    db = connect_db()
    data_db = db[collection]

    if duplicate_allowed:
        result = data_db.insert_one(doc)
        return {'status': True, 'message': result}
    else:
        try:
            result = data_db.insert_one(doc)
            return {'status': True, 'message': result}
        except pymongo.errors.DuplicateKeyError:
            return {'status': False, 'message': 'DUP'}

def update_one(collection=None, key=None, doc=None, upsert=False):
    db = connect_db()
    data_db = db[collection]

    result = data_db.update_one(key, doc, upsert=upsert)
    return {'status': result}

def get_if_array_contains(collection=None, values=[], owner=None, projection={}):
    db = connect_db()
    data_db = db[collection]
    projection['_id'] = 0
    
    result = list(data_db.find({"$or": [{'groups': {"$in":values}}, {owner:owner}]}, projection))

    if result is None:
        return {'status': False, 'data': None}
    else:
        return {'status': True, 'data': result}

def check_session():
    cookies = cookie_manager.get_all()
    
    if st.secrets["application"]["app_key"] in cookies:
        st.session_state.authenticated = True
        st.session_state.username = cookies[st.secrets["application"]["app_key"]]
        with st.sidebar:
            logout_submitted = st.button("Logout", type="primary")
            if logout_submitted:
                logout(cookies[st.secrets["application"]["app_key"]])
        return cookies[st.secrets["application"]["app_key"]]
    else:
        st.session_state.authenticated = False
        return None

def logout(username):
    st.cache_resource.clear()
    st.cache_data.clear()

    for key in st.session_state.keys():
        print ("Session key", key)
        del st.session_state[key]
        
    #if 'authenticated' in st.session_state:
    #    del st.session_state['authenticated']
    cookie_manager.delete(st.secrets["application"]["app_key"])
    r.delete(username)
    st.switch_page(" ")
    if 'delete' in st.session_state:
        st.rerun()

def login():
    l1, l2, l3 = st.columns([2,1.5,2])
    with l2:
        st.markdown("""<div style='padding-top:5rem'/>""", unsafe_allow_html=True)
        with st.form("login"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password",type='password')

            login_submitted = st.form_submit_button("Login")
        if login_submitted:
            result = check_password(username, password)
            if result == -1:
                st.error("Authentication failed. Please try again")

        
            elif result is not None:
                cookie_manager.set('dataraft', username)
                st.session_state.authenticated = True
                r.set(username, 'authenticated')
                key = f'_{st.secrets["application"]["app_key"]}_username'
                st.write("Logging in")
                #st.rerun()
            
                
            else:
                st.session_state.status = "incorrect"
                st.warning("Incorrect password. Please try again.")
                
                
            if 'status' in st.session_state and st.session_state.status == "incorrect":
                st.warning("Incorrect password. Please try again.")