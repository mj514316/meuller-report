#From spacy documentation
from spacy.matcher import PhraseMatcher
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import networkx as nx
import pandas as pd
from collections import Counter
from pyvis.network import Network
import re

class EntityMatcher(object):
    name = "entity_matcher"

    def __init__(self, nlp, terms, label):
        patterns = [nlp.make_doc(text) for text in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = Span(doc, start, end, label=match_id)
            doc.ents = list(doc.ents) + [span]
        return doc
    
    
def makeGraphFromSpacy(nlpList, minConnections = 1):
    """ Takes a list of document objects returned from sPaCy.
        Iterates through, takes the GPE, Person, and custom Themes from
        the spacy entities to construct the graph. Edges of the graph
        represent how often it occured, size of each node is fixed to degree
    """
    G = nx.Graph()
    colorMap = {'GPE':'Blue','PERSON':'Red','ORG':'Green','THEME':'Black'}

    for parNum, doc in enumerate(nlpList[0:len(nlpList)]):
        G.add_node(f"par_{parNum}", t = 'Paragraph', color = 'grey', text = doc.text) # Add a node for each paragraph
        #Get a count of all of the distinct occurences of an entity
        entCountDict = Counter([(ent.string.strip(),ent.label_) 
                                for ent in doc.ents 
                                if not bool(re.search(r":|\.", ent.text))  
                                and (ent.label_=='GPE' or 
                                     ent.label_ =='PERSON' or 
                                     ent.label_ =='THEME')])
        for ent,cnt in entCountDict.items():
            G.add_node(ent[0],label = ent[1], color = colorMap[ent[1]])
            #set the weight of the edge equal to the count of occurance
            G.add_edge(ent[0],f"par_{parNum}", weight = cnt)

    #minConnections allows you to prune the tree
    nodesToRemove = []
    for node in G.nodes():
        nodeDegree = G.degree(node)
        if nodeDegree >= 1:
            G.node[node]['value'] = nodeDegree
        else:
            nodesToRemove.append(node)

    for node in nodesToRemove:
        G.remove_node(node)
    G.number_of_nodes()
    return G

def from_nx(graphVizNet, nx_graph):
    """
    Custom from_nx function which captures colorls and titles. 
    This method is a bit fragile and highly dependant on the structure of the graph.
    I need to work to generalize
    """
    assert(isinstance(nx_graph, nx.Graph))
    edges = nx_graph.edges(data=True)
    nodes = nx_graph.nodes()
    if len(edges) > 0:
        for e in edges:
            #print('text' in nx_graph.node[e[0]] )
            graphVizNet.add_node(e[0], 
                label = str(e[0]), 
                title = multi_line_toolip(nx_graph.node[e[0]]['text']) if 'text' in nx_graph.node[e[0]] else e[0], 
                color = nx_graph.node[e[0]]['color'], 
                value = nx_graph.node[e[0]]['value']
            )

            graphVizNet.add_node(e[1], 
                label = e[1], 
                title = multi_line_toolip(nx_graph.node[e[1]]['text']) if 'text' in nx_graph.node[e[1]] else e[1],
                color = nx_graph.node[e[1]]['color'], 
                value = nx_graph.node[e[1]]['value']
            )

            graphVizNet.add_edge(e[0], e[1], value = nx_graph.edges[e[0],e[1]]['weight'])
    else:
        graphVizNet.add_nodes(nodes)
    return graphVizNet
def multi_line_toolip(aString: str):
    return(f'<a href="#" title="Line 1&#5;Line 2&#5;Line 3"> {aString}</a>')

def getFirstOrderGraph(graph, node):
    nodes = []
    [nodes.append(n) for n in graph.neighbors(node)]
    nodes += [node]
    subG = graph.subgraph(nodes)
    print(f"Nodes: {subG.number_of_nodes()}")
    print(f"Edges: {subG.number_of_edges()}")
    print(f"Self Loops: {subG.number_of_selfloops()}")
    return subG

def getSecondOrderSubgraph(graph, node):

    nodes = []
    for neighbor_list in [graph.neighbors(n) for n in graph.neighbors(node)]:
        for n in neighbor_list:
            nodes.append(n)
    nodes += [n for n in graph.neighbors(node)]
    subG = graph.subgraph(nodes)
    print(f"Nodes: {subG.number_of_nodes()}")
    print(f"Edges: {subG.number_of_edges()}")
    print(f"Self Loops: {subG.number_of_selfloops()}")
    return subG

def visualizeGraph(nxGraph, save = False, size = ['500px','500px']):
    """ Converts from networkx to a pyvis Network. 
    """
    subGViz = Network(size[0], size[1])
    from_nx(subGViz,nxGraph)
    
    if save:
        subGViz.save_graph(save)
    else:
        subGViz.write_html('graph.html')
        #subGViz.show('subGViz.html')
    return subGViz

def build_trimmed_subgraph(fullGraph, entity, n = 100000):
    """ 
    Takes an nx graph and a node name
    gets second order subgraph 
    and trims based on pagerank. 
    """
    subG = getSecondOrderSubgraph(fullGraph,entity)
    
    closeness = nx.algorithms.pagerank(subG)
    top_n_closeness = pd.DataFrame([closeness]).T.sort_values(0, ascending=False).head(n).reset_index()
    
    limited_sub_g = subG.subgraph(list(top_n_closeness['index']) + [entity])
    
    return limited_sub_g