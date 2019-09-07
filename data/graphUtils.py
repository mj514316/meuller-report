#From spacy documentation
from spacy.matcher import PhraseMatcher
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import networkx
from collections import Counter
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
    G = networkx.Graph()
    colorMap = {'GPE':'Blue','PERSON':'Red','ORG':'Green','THEME':'Black'}

    for parNum, doc in enumerate(nlpList[0:len(nlpList)]):
        G.add_node(f"par_{parNum}", t = 'Paragraph', color = 'grey') # Add a node for each paragraph
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
        if nodeDegree >= 0:
            G.node[node]['value'] = nodeDegree
        else:
            nodesToRemove.append(node)

    for node in nodesToRemove:
        G.remove_node(node)
    G.number_of_nodes()
    return G

def from_nx(graphVizNet, nx_graph):
    assert(isinstance(nx_graph, networkx.Graph))
    edges = nx_graph.edges(data=True)
    nodes = nx_graph.nodes()
    if len(edges) > 0:
        for e in edges:
            graphVizNet.add_node(e[0], e[0], title=str(e[0]), color = nx_graph.node[e[0]]['color'], value = nx_graph.node[e[0]]['value'])
            graphVizNet.add_node(e[1], e[1], title=str(e[1]), color = nx_graph.node[e[1]]['color'], value = nx_graph.node[e[1]]['value'])
            graphVizNet.add_edge(e[0], e[1], value = nx_graph.edges[e[0],e[1]]['weight'])
    else:
        graphVizNet.add_nodes(nodes)
    return graphVizNet

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