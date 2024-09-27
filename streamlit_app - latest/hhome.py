import streamlit as st
from streamlit.components.v1 import html
import extra_streamlit_components as stx
from streamlit_navigation_bar import st_navbar
from fixedContainer import st_fixed_container

# pager = {
#     "🗄️ Data": "Dataraft2.py",
#     "🚀 Quick Insights": "pages/Configure Data.py",
#     "🗂️ Pre-Proc Analysis": "pages/Project.py",
#     "📚 Explore": "pages/Explore.py",
#     "🕹️ Simulation": "pages/Explore.py",
#     "🔬 Experiment": "Explore.py",
#     "📈 Dashboards/Reports": "Explore.py"
# }
# def navbar():
#     page = st_navbar(
#     pages=list(pager),
#     styles={
#         'nav': {
#             'background-color': 'black',
#             'align-items': 'center',
#         },
#         'ul': {
#             'display': 'flex',
#             'justify-content': 'space-between'
#         },
#         'li': {
#             'flex': '1',
#             'text-align': 'center'
#         },
#         'span': {
#             'color': 'red'
#         }
#     },
#     adjust=True
# )
def navbar():
    
    with st_fixed_container(border=True): 
        h1,h2,h3,h5,h6,h7,h8,h9 = st.columns([0.6, 0.6, 0.6,0.8,0.8,0.8,0.6,0.8])
        with h1:
            st.page_link('Dataraft2.py', label='Data', icon='🗄️')
        with h2:
            st.page_link('pages/Explore.py', label='Explore', icon='🚀')
        with h3:
            st.page_link('pages/Analysis.py',label='Analysis', icon='🗂️')
        with h5:
            st.page_link('pages/Explore.py',label='Simulation', icon='🕹️')
        with h6:
            st.page_link('pages/Explore.py',label='Experiment', icon='🔬')
        with h7:
            st.page_link('pages/Explore.py',label='Dashboard', icon='🗺️')
        with h8:
            st.page_link('pages/Explore.py',label='Reports', icon='📈')
        with h9:
            st.page_link('pages/Explore.py',label='Optimization', icon='🛠')