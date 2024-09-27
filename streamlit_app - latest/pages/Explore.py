import streamlit_antd_components as sac
import streamlit as st
import pandas as pd
import duckdb
import streamlit.components.v1 as components
import hydralit_components as hc
import json
from itertools import combinations
from streamlit_extras.stylable_container import stylable_container
import matplotlib.pyplot as plt
import chart_config
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

st.markdown("""
        <style>
        .st-emotion-cache-6qob1r.eczjsme3 {
            background-color:#F0F2F6;
        }
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

st.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)

agg_functions = ['Count', 'Sum', 'Avg', 'Median'] 
chart_types = ['Bar', 'Pie', 'Grouped Bar', 'Stacked Bar', 'Line', 'Scatter', 'Bubble', 'Histogram']
weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
ticks = {'Month': months, 'Weekday': weekdays, 'Quarter': quarters}

def compute_histogram_bins(data, desired_bin_size):
    min_val = np.min(data)
    max_val = np.max(data)
    min_boundary = -1.0 * (min_val % desired_bin_size - min_val)
    max_boundary = max_val - max_val % desired_bin_size + desired_bin_size
    n_bins = int((max_boundary - min_boundary) / desired_bin_size) + 1
    bins = np.linspace(min_boundary, max_boundary, n_bins)
    return bins

def apply_theme(cplot, theme=None):
    #cplot.set_fc((1,1,1,0))
    #cplot.figure.patch.set_alpha(0)
    cplot.grid(visible=False)

    #cplot.xaxis.label.set_color('white')
    #cplot.yaxis.label.set_color('white')
    #cplot.tick_params(colors='white', which='both') 
    #cplot.figure.patch.set_facecolor('xkcd:mint green')
    return cplot

#        {name: 'Variance', value: 'var'},
#        {name: 'Minimum', value: 'min'},
#        {name: 'Maximum', value: 'max'},
#        {name: 'First', value: 'first'},
#3        {name: 'Last', value: 'last'},
#3        {name: 'Sum as Fraction of Total', value: 'sum'},
#        {name: 'Skewness', value: 'skewness'},
#        {name: 'Kurtosis', value: 'kurtosis'},
#        {name: 'Median Absolute Deviation', value: 'mad'},
#        {name: 'Entropy', value: 'entropy'}

if 'start' not in st.session_state:
    st.session_state['start'] = 0
if 'end' not in st.session_state:
    st.session_state['end'] = 25

LIMIT = 25

menu_data = [
        {'id':'Workspace', 'icon': "far fa-copy", 'label':"Workspace"},
        {'icon': "far fa-copy", 'label':"Trends"},
        {'icon': "far fa-chart-bar", 'label':"Inferences"},
        {'icon': "far fa-chart-bar", 'label':"Chart"},
        {'icon': "far fa-address-book", 'label':"Pivot"},
        {'icon': "far fa-chart-bar", 'label':"Timeseries"},
]

over_theme = {'txc_inactive': '#FFFFFF'}

over_theme = {'txc_inactive': 'black','menu_background':'lightblue','txc_active':'yellow','option_active':'grey', 'padding-top': '0rem'}
font_fmt = {'font-class':'h2','font-size':'100%'}

#menu_id = hc.nav_bar(menu_definition=menu_data,home_name='Dataset',override_theme=over_theme, sticky_nav=True, sticky_mode='pinned')
widget_id = (id for id in range(1, 100_00))

def summarize():
    user = util.get_user(st.session_state.username)
    organization = util.get_one_item(collection='organization', organization=user['organization'])
    datasets = util.get_if_array_contains(collection='datasets', values=user['groups'], owner=user['username'])
    user_datasets = [item['name'] for item in datasets['data']] 

    with st.sidebar:
        st.markdown("### :blue[Choose Workspace]")
        selected_dataset = st.selectbox('', user_datasets, label_visibility="hidden", index=None)
    
    menu_id = hc.option_bar(option_definition=menu_data,key='PrimaryOption',override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

    with st.sidebar:
        if selected_dataset and menu_id not in ['Workspace', 'Timeseries', 'Pivot']:
            filter_container = st.container(border=True)
            with filter_container:
                filtering_condition = st.text_input("Filter", '', key=next(widget_id))
                filter_expression = 'where '
                if filtering_condition != '':
                    filter_expression += f" {filtering_condition}"
                
                if filter_expression.strip() == 'where':
                    filter_expression = ''

    if selected_dataset is None:
        st.markdown("#### :red[Please choose a workspace on the sidebar to continue.]")

    if selected_dataset is not None:
        ducon = duckdb.connect(database=f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}.duckdb', read_only=True)
        schema = ducon.sql(f'describe {selected_dataset}').df()
        st.session_state.dataset_columns = schema['column_name'].values.tolist()

    if menu_id == 'Workspace' and selected_dataset is not None:
        where_condition = ''
        if 'condition' in st.session_state:
            where_condition = f' where {st.session_state["condition"]}'
            if where_condition.strip() == 'where':
                where_condition = ''
        else:
            st.session_state["condition"] = ''
                
        try:
            df = ducon.sql(f'select * from {selected_dataset} {where_condition} order by rowId offset {st.session_state["start"]} limit {st.session_state["end"]}').df()
            
            with st.sidebar:
                options = st.multiselect('', df.columns.tolist(), df.columns.tolist(), label_visibility="collapsed")
                
            st.dataframe(df[options])
            pagination = st.container()
            bottom_menu = st.columns((4, 0.30))
            with bottom_menu[1]:
                col1, col2 = st.columns((0.5,0.5))
                with col1:
                    if st.button(label=':arrow_backward:'):
                        if st.session_state["start"] > 0:
                            st.session_state["start"] = st.session_state["start"] - LIMIT
                            st.rerun()
                with col2:
                    if st.button(label=':arrow_forward:'):
                        if st.session_state["start"] + LIMIT < st.session_state['rowcount']:
                            st.session_state["start"] += LIMIT
                        st.rerun()
                #batch_size = st.selectbox("Page Size", options=[25, 50, 100])
            with bottom_menu[0]:
                col1, col2 = st.columns([3,1])
                with col1:
                    condition = st.text_input(
                        "Input selection condition",
                        st.session_state["condition"],
                        key="placeholder",
                        label_visibility="collapsed"
                    )
                with col2:
                    if st.button('Run'):
                        st.session_state["condition"] = condition
                        st.rerun()
                    else:
                        pass
        except Exception as e:
            st.write(e)
            st.error("Error encoutered executing your query. Check your condition!")
    try:
        if menu_id == 'Trends' and selected_dataset is not None:
            schema = ducon.sql(f'describe {selected_dataset}').df()
            #numericals = schema[schema['column_type'] == 'FLOAT']['column_name'].values.tolist()
            numericals = schema[schema['column_type'] == 'VARCHAR']['column_name'].values.tolist()
            st.write(numericals)
            df = ducon.sql(f'select {",".join(numericals)} from {selected_dataset} {filter_expression}').df()
            col_count = len(df.columns)
            st.session_state.dataset_columns = df.columns.values.tolist()
            i = 0
            while i < col_count:
                col1, col2, col3 = st.columns([1,1,1])
                with col1:
                    with st.container(border=True):
                        st.write(f'Trend for {df.columns[i]}')
                        st.line_chart(data=df[df.columns[i]], y=df.columns[i])
                    i += 1
                if i < col_count:
                    with col2:
                        with st.container(border=True):
                            st.write(f'Trend for {df.columns[i]}')
                            st.line_chart(data=df[df.columns[i]], y=df.columns[i])
                        i += 1
                if i < col_count:
                    with col3:
                        with st.container(border=True):
                            st.write(f'Trend for {df.columns[i]}')
                            st.line_chart(data=df[df.columns[i]], y=df.columns[i])
                        i += 1
                    
            st.line_chart(df)
    except Exception as e:
        st.error("No trends to show if the data is non numeric/inappropriate/insufficient")

    if menu_id == 'Inferences' and selected_dataset is not None:
        
        tabs = sac.tabs([sac.TabsItem(label='Descriptive'),sac.TabsItem(label='Combinatorial'),sac.TabsItem(label='Advanced')],align='left',color='blue')
        if tabs=='Descriptive':
            try:
                if selected_dataset is not None:
                    schema = ducon.sql(f'describe {selected_dataset}').df()
                    st.session_state.dataset_columns = schema['column_name'].values.tolist()
                    categoricals = schema[schema['column_type'] == 'VARCHAR']['column_name'].values.tolist()
                    col_count = len(categoricals)
                    row_count = ducon.sql(f'select count(*) as count from {selected_dataset}').fetchall()[0][0]

                    i = 0
                    while i < col_count:
                        col1, col2, col3 = st.columns([1,1,1])
                        with col1:
                            while i < col_count:
                                    df = ducon.sql(f'select {categoricals[i]}, count({categoricals[i]}) as count from {selected_dataset} {filter_expression} group by {categoricals[i]}').df()
                                    if len(df['count']) != row_count:
                                        st.bar_chart(data=df, x=categoricals[i], y='count')
                                        i += 1
                                        break
                                    else:
                                        i += 1
                                
                        if i < col_count:
                            with col2:
                                while i < col_count:
                                    df = ducon.sql(f'select {categoricals[i]}, count({categoricals[i]}) as count from {selected_dataset} {filter_expression} group by {categoricals[i]}').df()
                                    if len(df['count']) != row_count:
                                        st.bar_chart(data=df, x=categoricals[i], y='count')
                                        i += 1
                                        break
                                    else:
                                        i += 1
                        if i < col_count:
                            with col3:
                                while i < col_count:
                                    df = ducon.sql(f'select {categoricals[i]}, count({categoricals[i]}) as count from {selected_dataset} {filter_expression} group by {categoricals[i]}').df()
                                    if len(df['count']) != row_count:
                                        st.bar_chart(data=df, x=categoricals[i], y='count')
                                        i += 1
                                        break
                                    else:
                                        i += 1
            except Exception as e:
                st.error("The file contains empty data or is too big or is corrupted. Please try again")
            def colorify(val):
                return f'background-color: rgba(255,200,19,{abs(val)});'
            
            schema = ducon.sql(f'describe {selected_dataset}').df()
            numericals = schema[schema['column_type'] == 'FLOAT']['column_name'].values.tolist()
            pairs = combinations(numericals, 2)
            sql = ''
            for pair in pairs:
                sql += f'corr{str(pair)} as "{pair[0]} vs. {pair[1]}",'
            sql = sql.replace("'", "")
            
            if sql != '':
                corr_df = ducon.sql(f'select {sql} from {selected_dataset} {filter_expression}').df()
                transposed = corr_df.transpose()
                transposed = transposed.rename_axis('Variables', axis=0)
                transposed = transposed.rename(columns={'':'Variables', 0: 'Correlation'})
                st.dataframe(transposed.style.applymap(colorify, subset=['Correlation']))
        if tabs=='Combinatorial':
            st.info("We will be showing graphs of categorical and numerical combinations")
        if tabs=='Advanced':
            st.info("We will be displaying tests like ANOVA, Factorial Analysis, etc.")
    try:
        if menu_id == 'Chart' and selected_dataset is not None:
            schema = ducon.sql(f'describe {selected_dataset}').df()
            #categoricals = schema[schema['column_type'] == 'VARCHAR']['column_name'].values.tolist()
            categoricals = schema['column_name'].values.tolist()
            for i in range(len(categoricals)):
                if '(' in categoricals[i] or ')' in categoricals[i]:
                    categoricals[i] = f'"{categoricals[i]}"'
            # st.write(categoricals)
            #the reason for doing the above i.e, converting every list item containing brackets to a string is because it considers the brackets as a function and gives an error
            categoricals = ['None'] + categoricals
            numericals = schema[schema['column_type'] == 'FLOAT']['column_name'].values.tolist()
            periodicals = schema[schema['column_type'] == 'DATE']['column_name'].values.tolist()
            periodicals = ['None'] + periodicals

            x_group_option = ''
            sql = ''
            with st.sidebar:
                chart_option = st.selectbox('Chart', chart_types, key=next(widget_id))
                if chart_option == 'Line':
                    series_options = st.multiselect('Series', numericals, [])
                elif chart_option == 'Pie':
                    inner_radius = st.number_input(value=0, label='Donut Hole', key=next(widget_id))
                    sort_option = st.radio("Sort", ["Orig", "Asc", "Desc"], index=None, horizontal=True, key=next(widget_id))
                elif chart_option == 'Bar':
                    sort_option = st.radio("Sort", ["Orig", "Asc", "Desc"], index=0, horizontal=True, key=next(widget_id))
                    orientation_option = st.radio("Orient", ["Vertical", "Horizontal"], index=0, horizontal=True, key=next(widget_id))
                elif chart_option == 'Histogram':
                    distribution_option = st.selectbox('Distribution', numericals, key=next(widget_id))
                    #with_density = st.toggle('Density Plot')
                elif chart_option in ['Grouped Bar', 'Stacked Bar']:
                    sort_option = st.radio("Sort", ["Orig", "Asc", "Desc"], index=None, horizontal=True, key=next(widget_id))

                if chart_option not in ['Histogram']:
                    x_option = st.selectbox('X', categoricals + numericals, key=next(widget_id))
                if chart_option in ['Grouped Bar', 'Stacked Bar']:
                    x_group_option = st.selectbox('X Group', categoricals + numericals, key=next(widget_id))

                if chart_option in ['Bar', 'Pie', 'Bubble', 'Scatter', 'Grouped Bar', 'Stacked Bar']:
                    y_option = st.selectbox('Y', categoricals + numericals, key=next(widget_id))
                if chart_option in ['Bubble']:
                    z_option = st.selectbox('Z', numericals, key=next(widget_id))
                
                if chart_option in ['Line']:
                    time_option = st.selectbox('Time', periodicals, key=next(widget_id))

                if chart_option in ['Bar', 'Pie', 'Grouped Bar', 'Stacked Bar']:
                    agg_option = st.selectbox('Aggregation', agg_functions, key=next(widget_id))
                    if chart_option == 'Bar':
                        if x_option != 'None' and y_option != 'None':
                            sql = f'select {x_option}, {agg_option}({y_option}) as {agg_option} from {selected_dataset} {filter_expression} group by {x_option}, {x_group_option}'
                    elif chart_option == 'Line':
                        if time_option == 'None':
                            if len(series_options) > 0:
                                if x_option == 'None':
                                    sql = f'select {",".join(series_options)} from {selected_dataset} {filter_expression}'
                                else:
                                    sql = f'select {x_option}, {",".join(series_options)} from {selected_dataset} {filter_expression}'
                        else:
                            sql = f'select {time_option}, {",".join(series_options)} from {selected_dataset}'
                    elif chart_option == 'Pie':
                        if x_option != 'None' and y_option != 'None':
                            sql = f'select {x_option}, {agg_option}({y_option}) as {agg_option} from {selected_dataset} {filter_expression} group by {x_option}, {x_group_option}'
                    elif chart_option in ['Grouped Bar', 'Stacked Bar']:
                        if x_option != 'None' and y_option != 'None' and x_group_option != 'None':
                            sql = f'select {x_option}, {x_group_option}, {agg_option}({y_option}) as {agg_option} from {selected_dataset} {filter_expression} group by {x_option}, {x_group_option}'
                    elif chart_option in ['Scatter']:
                        if x_option != 'None' and y_option != 'None':
                            sql = f'select {x_option}, {y_option} from {selected_dataset} {filter_expression}'
                    elif chart_option in ['Bubble']:
                        sql = f'select {x_option}, {y_option}, {z_option} from {selected_dataset} {filter_expression}'
                    elif chart_option in ['Histogram']:
                        sql = f'select {distribution_option} from {selected_dataset} {filter_expression}'

            if sql != '':
                    df = ducon.sql(sql).df()
                    if chart_option not in ['Histogram']:
                        with_datatable = st.checkbox('Show data table')
                    col1, col2 = st.columns([2,1])
                    with col1:
                        if chart_option not in ['Scatter', 'Bubble', 'Line', 'Histogram']:
                            if sort_option != 'Orig':
                                order = True if sort_option == 'Asc' else False
                                df.sort_values(by=[agg_option], inplace=True, ascending=order)
                        chart_data = json.loads(df.to_json(orient='records'))
                        if chart_option == 'Line':
                            config = chart_config.line_chart()
                            if time_option == 'None':
                                if x_option == 'None':
                                    st.line_chart(data=df, y=df.columns, width=700, height=500)
                                else:
                                    config['data']['values'] = chart_data
                                    config['encoding']['x']['field'] = x_option
                                    config['encoding']['x']['type'] = 'nominal'
                                    config['encoding']['y']['field'] = series_options[0]
                                    #config['encoding']['color']['field'] = x_option
                                    #config['encoding']['color']['type'] = 'nominal'
                                    #st.write(config)
                                    #st.vega_lite_chart(config)
                                    st.line_chart(data=df, x=x_option, y=list(set(df.columns)-set([x_option])), width=700, height=500)
                                    #st.line_chart(data=df, x=x_option, y=list(set(df.columns)-set([x_option])))
                            else:
                                st.line_chart(data=df, x=time_option, y=list(set(df.columns)-set([time_option])), width=700, height=500)
                        elif chart_option == 'Pie':
                            config = chart_config.pie_chart()
                            config['mark']['innerRadius'] = inner_radius
                            config['encoding']['color']['sort'] = "ascending"
                            config['encoding']['theta']['field'] = agg_option
                            config['encoding']['color']['field'] = x_option
                            config['data']['values'] = chart_data
                            st.vega_lite_chart(config)
                        elif chart_option == 'Bar':
                            config = chart_config.bar_chart()
                            config['data']['values'] = chart_data
                            if orientation_option is None:
                                orientation_option = 'vertical'
                            #config['mark']['orient'] = orientation_option.lower()
                            config['encoding']['x']['field'] = x_option
                            config['encoding']['y']['field'] = agg_option
                            #config['encoding']['y']['type'] = 'nominal'
                            if orientation_option == 'Horizontal':
                                y_temp = config['encoding']['y']
                                config['encoding']['y'] = config['encoding']['x']
                                config['encoding']['x']  = y_temp
                            if sort_option == "Asc":
                                if orientation_option == 'Horizontal':
                                    config['encoding']['y']['sort'] = "x"
                                elif orientation_option == 'Vertical':
                                    config['encoding']['x']['sort'] = "y"
                            elif sort_option == "Desc":
                                if orientation_option == 'Horizontal':
                                    config['encoding']['y']['sort'] = "-x"
                                elif orientation_option == 'Vertical':
                                    config['encoding']['x']['sort'] = "-y"
                            st.vega_lite_chart(config)
                        elif chart_option == 'Grouped Bar':
                            if x_option != 'None' and x_group_option != 'None' and y_option != 'None':
                                config = chart_config.grouped_bar_chart()
                                config['data']['values'] = chart_data
                                config['encoding']['x']['field'] = x_option
                                config['encoding']['y']['field'] = agg_option
                                config['encoding']['xOffset']['field'] = x_group_option
                                config['encoding']['color']['field'] = x_group_option
                                st.vega_lite_chart(config)
                        elif chart_option == 'Stacked Bar':
                            if x_option != 'None' and x_group_option != 'None' and y_option != 'None':
                                config = chart_config.stacked_bar_chart()
                                config['data']['values'] = chart_data
                                config['encoding']['x']['field'] = x_option
                                config['encoding']['y']['field'] = agg_option
                                config['encoding']['color']['field'] = x_group_option
                                st.vega_lite_chart(config)
                        elif chart_option == 'Scatter':
                            if x_option != 'None' and y_option != 'None':
                                config = chart_config.scatter_plot()
                                config['data']['values'] = chart_data
                                config['encoding']['x']['field'] = x_option
                                config['encoding']['y']['field'] = y_option
                                st.vega_lite_chart(config)
                        elif chart_option == 'Bubble':
                            config = chart_config.bubble_plot()
                            config['data']['values'] = chart_data
                            config['encoding']['x']['field'] = x_option
                            config['encoding']['y']['field'] = y_option
                            config['encoding']['y']['axis']['title'] = y_option
                            config['encoding']['size']['field'] = z_option
                            config['encoding']['size']['title'] = z_option
                            config['encoding']['color']['field'] = z_option
                            st.vega_lite_chart(config)
                        elif chart_option == 'Histogram':
                            config = chart_config.histogram()
                            config['data']['values'] = chart_data
                            config['encoding']['x']['field'] = distribution_option
                            
                            #if with_density:
                            #    config['mark'] = 'area'
                            #    config['encoding']['y']['field'] = "density"
                            #    config['encoding']['y']['type'] = "quantitative"
                            #    config["transform"] = [{"density": distribution_option, "bandwidth": 0.3}]

                            bins = compute_histogram_bins(df[distribution_option].values.tolist(), 2.5)
                            
                            #ax = df[df.columns.tolist()].plot(kind='kde')
                            ax = df.plot(kind='hist', bins=bins)
                            ax.set_fc((1,1,1,0))
                            skew = json.loads(df.skew().to_json())
                            kurt = json.loads(df.kurt().to_json())
                            hist = df.plot(kind='kde', ax=ax, secondary_y=True)
                            label = ''.join([f'Skewness:{round(skew[c],3)}, Kurtosis:{round(kurt[c],3)}' for c in df.columns])
                            ax.set_xlabel(label)
                            ax.spines['bottom'].set_color('blue')
                            ax.spines['top'].set_color('red') 
                            ax.spines['right'].set_color('white')
                            ax.spines['right'].set_linewidth(3)
                            ax.spines['left'].set_color('white')
                            ax.spines['left'].set_lw(3)
                            ax.xaxis.label.set_color('purple')
                            ax.yaxis.label.set_color('silver')
                            ax.tick_params(colors='red', which='both') 
                            
                            #ax.figure.set_size_inches(20, 10)
                            hist.figure.patch.set_facecolor('xkcd:mint green')
                            hist.figure.patch.set_alpha(0)
                            #g1, g2 = st.columns((20,4))
                            st.pyplot(hist.figure)
                            #with g1:
                            #with g2:
                            #    st.vega_lite_chart(config)

                    with col2:
                        if chart_option not in ['Histogram']:
                            if with_datatable:
                                st.dataframe(df)
    except Exception as e:
        st.error("You have selected wrong combination of parameters/ dataset is non-numeric/ the data is empty. Please try again!")            

    if menu_id == 'Timeseries' and selected_dataset is not None:
        schema = ducon.sql(f'describe {selected_dataset}').df()
        categoricals = schema[schema['column_type'] == 'VARCHAR']['column_name'].values.tolist()
        categoricals = ['None'] + categoricals
        numericals = schema[schema['column_type'] == 'FLOAT']['column_name'].values.tolist()
        numericals = ['None'] + numericals
        periodicals = schema[schema['column_type'] == 'DATE']['column_name'].values.tolist()
        periodicals = ['None'] + periodicals
        sql = ''
        
        with st.sidebar:
            periodical_option = st.selectbox('Date', periodicals, key=next(widget_id))
            y_option = st.selectbox('Y', numericals, key=next(widget_id))
            category_option = st.selectbox('Category', categoricals, key=next(widget_id))
            if category_option != 'None':
                category_values = ducon.sql(f'select distinct {category_option} from {selected_dataset}').df()[category_option].values.tolist()
                category_value = st.selectbox('Category Value', category_values, key=next(widget_id))

        where_condition = 'where '
        if category_option != 'None' and category_value != 'None':
            where_condition += f" {category_option} == '{category_value}'"
        
        if where_condition.strip() == 'where':
            where_condition = ''
        
        if periodical_option != 'None' and y_option != 'None':
            sql = f"select {periodical_option}, {y_option} from {selected_dataset} {where_condition}"

        if sql != '':
            df = ducon.sql(sql).df()
            df = df.set_index(periodical_option)
            df['Year'] = df.index.year
            df['Month'] = df.index.month_name()
            df['Weekday'] = df.index.day_name()
            df['Quarter'] = df.index.quarter
            df['Quarter'] = 'Q' + df['Quarter'].astype(str)
            #sns.set(rc={'figure.figsize':(10, 4)})
            ysmoothed = gaussian_filter1d(df[y_option], sigma=2)
            #plot = plt.plot(df[y_option], ysmoothed)
            #df['spline'] = BSpline(*tck)(df[[y_option]])
            
            plot = df[[y_option]].plot(linewidth=0.5)
            #plot.plot(xnew, BSpline(*tck)(df[[y_option]]), '-', label='s=0')
            #plot.set_fc((1,1,1,0))
            #plot.figure.patch.set_alpha(0.5)
            plot.grid(visible=False)

            #plot.xaxis.label.set_color('white')
            #plot.yaxis.label.set_color('white')
            plot.tick_params(which='both') 
            #plot.figure.patch.set_facecolor('xkcd:mint green')
            st.pyplot(plot.figure)
            
            
            for key in ["Year", "Month", "Weekday", "Quarter"]:
                fig, ax = plt.subplots(1, constrained_layout=True, figsize=(10,5))
                #sns.set(style="ticks")
                df_group = df.groupby(key).agg(sum=(y_option, np.sum))
                line = sns.lineplot(data=df_group, x=key, y='sum', marker="o", markers=True, ax=ax, estimator=None, linewidth=2)
                ax.set_ylabel(y_option)
                for i, txt in enumerate(df_group.to_records()):
                    if i % 1 == 0:
                        line.text(txt[0], txt[1], txt[1])
                    if key in ["Month", "Weekday", "Quarter"]:
                        line.set_xticklabels(ticks[key])

                ax = apply_theme(ax)                    
                st.pyplot(fig)
            
            st.dataframe(df)

    if menu_id == 'Pivot' and selected_dataset is not None:
        schema = ducon.sql(f'describe {selected_dataset}').df()
        st.session_state.dataset_columns = schema['column_name'].values.tolist()
        on_columns = schema[schema['column_type'] == 'VARCHAR']['column_name'].values.tolist()
        numericals = schema[schema['column_type'] == 'FLOAT']['column_name'].values.tolist()
        col_count = len(on_columns)
        unique_cols = []
        try:
            unique_cols = json.load(open(f'{organization["dataPath"]}/{selected_dataset}/{selected_dataset}_unique_cols.json'))
        except:
            pass
        
        with st.sidebar:
            on_options = st.multiselect('On', on_columns, [], key=next(widget_id))
            using_option = st.selectbox('Using', numericals, index=None, key=next(widget_id))
            agg_option = st.selectbox('Aggregation', agg_functions, key=next(widget_id))
            group_by_options = st.multiselect('Group by', on_columns, [], key=next(widget_id))

        if len(on_options) > 0:
            sql = f'pivot {selected_dataset} on ({",".join(on_options)})'
            if using_option is not None:
                sql += f' using {agg_option}({using_option})'

            if len(group_by_options) > 0:
                sql += f' group by {",".join(group_by_options)}'
                
            df = ducon.sql(sql).df()
            df = df.append(df.sum(numeric_only=True), ignore_index=True)
            df['TOTAL'] = df.sum(axis=1)
            if len(group_by_options) > 0:
                df = df.set_index(group_by_options[0])

            st.caption(sql[0].upper() + sql[1:])
            st.dataframe(df) #, hide_index=True)
                   
    if selected_dataset and menu_id not in ['Dataset', 'Timeseries', 'Pivot']:
        with filter_container:
            if 'dataset_columns' in st.session_state:
                with st.popover("Variables"):
                    for col in st.session_state.dataset_columns:
                        st.code(col)

    st.write()
#st.bar_chart(df[['RouteArea', 'Weather']], columns=['RouteArea', 'Weather'])

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
        summarize()
    except duckdb.CatalogException as d:
        st.error("The duckdb file has been deleted/does not exist. Please try again!")