from grid_digraph_generator import GridDigraphGenerator
from steiner_tree_lp import SteinerTreeLP
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':
    gh = GridDigraphGenerator()
    graph = gh.generate(5, 5)
    terminals = []
    poi = None
    splp = SteinerTreeLP(graph, terminals, poi)
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph()
