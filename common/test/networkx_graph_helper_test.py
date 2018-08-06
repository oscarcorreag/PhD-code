from networkx_graph_helper import NetworkXGraphHelper
from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator

if __name__ == '__main__':
    # graph = {'a': {'b': 4, 'd': 3},
    #          'b': {'a': 4, 'd': 5, 'e': 3, 'f': 3, 'g': 4, 'c': 2},
    #          'c': {'b': 2, 'g': 1},
    #          'd': {'a': 3, 'b': 5, 'e': 1, 'f': 2, 'i': 1, 'h': 1},
    #          'e': {'d': 1, 'b': 3, 'f': 1},
    #          'f': {'e': 1, 'd': 2, 'b': 3, 'g': 2, 'i': 2},
    #          'g': {'f': 2, 'b': 4, 'c': 1, 'i': 3},
    #          'h': {'d': 1, 'i': 2},
    #          'i': {'f': 2, 'g': 3, 'd': 1, 'h': 2}}

    # graph = {'a': (1.2, {'b': 4, 'd': 3}),
    #          'b': (1.4, {'a': 4, 'd': 5, 'e': 3, 'f': 3, 'g': 4, 'c': 2}),
    #          'c': (1.1, {'b': 2, 'g': 1}),
    #          'd': (1.7, {'a': 3, 'b': 5, 'e': 1, 'f': 2, 'i': 1, 'h': 1}),
    #          'e': (1.2, {'d': 1, 'b': 3, 'f': 1}),
    #          'f': (1.8, {'e': 1, 'd': 2, 'b': 3, 'g': 2, 'i': 2}),
    #          'g': (1.1, {'f': 2, 'b': 4, 'c': 1, 'i': 3}),
    #          'h': (1.1, {'d': 1, 'i': 2}),
    #          'i': (1.4, {'f': 2, 'g': 3, 'd': 1, 'h': 2})}

    # graph = {
    #     'a': (1, {'b': 1, 'd': 1}),
    #     'b': (1, {'a': 1, 'c': 1, 'e': 1}),
    #     'c': (1, {'b': 1, 'f': 1}),
    #     'd': (1, {'a': 1, 'e': 1, 'g': 1}),
    #     'e': (1, {'d': 1, 'b': 1, 'f': 1, 'h': 1}),
    #     'f': (1, {'c': 1, 'e': 1, 'i': 1}),
    #     'g': (1, {'d': 1, 'h': 1}),
    #     'h': (1, {'g': 1, 'e': 1, 'i': 1}),
    #     'i': (1, {'h': 1, 'f': 1})
    # }

    seed = 1
    generator = SuitableNodeWeightGenerator()
    gh = GridDigraphGenerator()
    weighted_graph = gh.generate(10, 10, node_weighted=True, node_weight_generator=generator, seed=seed)

    ngh = NetworkXGraphHelper(weighted_graph)
    ngh.draw_graph()

    subgraph = ngh.get_node_induced_subgraph([12, 13, 63, 84])
    print(subgraph.edges())
