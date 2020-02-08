import dash
import dash_core_components as dcc
import dash_html_components as html
import sys
sys.path.append("../code/")
import networkx as nx
import pandas as pd
from graphUtils import from_nx, getFirstOrderGraph, getSecondOrderSubgraph, visualizeGraph, build_trimmed_subgraph
from pyvis.network import Network
from dash.dependencies import Input, Output

fullMeuller = nx.read_gpickle("../data/fullMeullerGraph.gpickle")


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div(children=[
    html.H1(children='Mueller Report'),	
	dcc.Dropdown(
        id='ent-dropdown',
		#options = [{'label':'Trump','value':'Trump'}],
        options=[{'label':n, 'value':n} for n in fullMeuller.nodes if not n.startswith('par')],
        value='Trump'
    ),
	html.Div("Select Number of Nodes to display:"),

	dcc.Slider(
		id = 'node-count',
		marks={i: '{}'.format(i) for i in range(5,100,5)},
		min=5,
		max=100,
		step=5,
		value=40
	),
	html.H3("Relationship Graph"),
	html.Div(id = 'out'),
	html.Iframe(id = 'graphOut', height = '600px', width = '600px'	)

])

@app.callback(
	Output('graphOut', 'srcDoc'),
	[Input(component_id  = 'ent-dropdown', component_property = 'value'), Input(component_id  = 'node-count', component_property = 'value')]
)
def table_update(search_term, node_count):
	sub_g = build_trimmed_subgraph(fullMeuller,search_term, n = node_count)
	sub_viz = visualizeGraph(sub_g)
	return sub_viz.html
# def print_input(theList, searchTerm):
# 	return f"Check Out This List: {theList}, and this search: {searchTerm}"

if __name__ == '__main__':
    app.run_server(debug=True)
