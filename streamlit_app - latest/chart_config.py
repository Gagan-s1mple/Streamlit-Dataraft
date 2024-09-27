import json

def pie_chart():
    return json.loads(open("./chart_data_templates/simple_pie.json").read())

def bar_chart():
    return json.loads(open("./chart_data_templates/simple_bar.json").read())

def grouped_bar_chart():
    return json.loads(open("./chart_data_templates/grouped_bar.json").read())

def stacked_bar_chart():
    return json.loads(open("./chart_data_templates/stacked_bar.json").read())

def scatter_plot():
    return json.loads(open("./chart_data_templates/scatter_plot.json").read())

def bubble_plot():
    return json.loads(open("./chart_data_templates/bubble_plot.json").read())

def line_chart():
    return json.loads(open("./chart_data_templates/line_chart.json").read())

def histogram():
    return json.loads(open("./chart_data_templates/histogram.json").read())