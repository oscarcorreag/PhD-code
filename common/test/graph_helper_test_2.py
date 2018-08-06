from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':
    gh = GridDigraphGenerator()
    graph = gh.generate(10, 10)
    subgraph = graph.extract_node_induced_subgraph([4, 8, 9, 10, 34, 38, 37, 66, 35, 65, 67])
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_subgraphs=[(subgraph, None)], print_node_labels=True)
