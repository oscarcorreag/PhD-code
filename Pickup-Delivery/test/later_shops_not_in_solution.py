from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import sample, CsdpAp
from digraph import Digraph
from random import shuffle


if __name__ == '__main__':
    # Show the initial set up.
    generator = GridDigraphGenerator()
    m = 30
    n = 35
    fraction_sd = .33
    graph = generator.generate(m, n, edge_weighted=False)
    helper = NetworkXGraphHelper(graph)