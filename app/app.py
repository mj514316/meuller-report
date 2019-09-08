import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/'
    'datasets/master/gapminderDataFiveYear.csv')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Test App W/Filtering'),
	dcc.Input(id = 'search', value = 'enter search here', type = 
'text'),
	dcc.Checklist(id = 'checkList',
		options = [
			{'label': 'People', 'value' : 'People'},
			{'label': 'Locations', 'value' : 'Locations'},
			{'label': 'Concepts', 'value' : 'Concepts'}
		],
		value = ['People','Locations']),
	dcc.Dropdown(
        id='my-dropdown',
        options=[{'label':thing, 'value':thing} for thing in list(df.country.unique())],
        value='Albania'
    )
	, dash_table.DataTable(
		id='my-table',
		columns=[
			{"name": i, "id": i} for i in sorted(df.columns)
		],
		page_current=0,
		page_size=2,
		page_action='custom'
	),
	html.Div(id = 'out')

])

@app.callback(
	Output('my-table', 'data'),
	[Input(component_id = 'checkList', component_property = 'value'),
	Input(component_id  = 'my-dropdown', component_property = 'value')]
)
def table_update(checkList, searchTerm):
	df1 = df[df['country'] == searchTerm].to_dict('records')
	print(searchTerm)
	return df1
# def print_input(theList, searchTerm):
# 	return f"Check Out This List: {theList}, and this search: {searchTerm}"

if __name__ == '__main__':
    app.run_server(debug=True)
