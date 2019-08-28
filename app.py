import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/'
    'datasets/master/gapminderDataFiveYear.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Meuller Report Graph Search'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
	dcc.Input(id = 'search', value = 'enter search here', type = 
'text'),
	dcc.Checklist(id = 'checkList',
		options = [
			{'label': 'People', 'value' : 'People'},
			{'label': 'Locations', 'value' : 'Locations'},
			{'label': 'Concepts', 'value' : 'Concepts'}
		],
		value = ['People','Locations']),
	html.Div(id = 'out')

])

@app.callback(
	Output(component_id = 'out', component_property = 'children'),
	[Input(component_id = 'checkList', component_property = 'value')]
)
def print_input(theList):
	return f"Check Out This List: {theList}"

if __name__ == '__main__':
    app.run_server(debug=True)
