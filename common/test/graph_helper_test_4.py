from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':
    gh = GridDigraphGenerator()
    graph = gh.generate(5, 5, edge_weighted=False)
    graph.perturb_edge_weights()
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph()