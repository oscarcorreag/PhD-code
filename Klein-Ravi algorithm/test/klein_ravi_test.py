from klein_ravi import KleinRavi
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitableNodeWeightGenerator


if __name__ == '__main__':
    # graph = {'a': (1.2, {'b': 4, 'd': 3}),
    #          'b': (1.4, {'a': 4, 'd': 5, 'e': 3, 'f': 3, 'g': 4, 'c': 2}),
    #          'c': (1.1, {'b': 2, 'g': 1}),
    #          'd': (1.7, {'a': 3, 'b': 5, 'e': 1, 'f': 2, 'i': 1, 'h': 1}),
    #          'e': (1.2, {'d': 1, 'b': 3, 'f': 1}),
    #          'f': (1.8, {'e': 1, 'd': 2, 'b': 3, 'g': 2, 'i': 2}),
    #          'g': (1.1, {'f': 2, 'b': 4, 'c': 1, 'i': 3}),
    #          'h': (1.1, {'d': 1, 'i': 2}),
    #          'i': (1.4, {'f': 2, 'g': 3, 'd': 1, 'h': 2})}
    #
    # terminals = ['b', 'c', 'e', 'h', 'i']

    seed = 6
    gh = GridDigraphGenerator()
    generator = SuitableNodeWeightGenerator()

    node_weighted = gh.generate(30, 30, node_weighted=True, node_weight_generator=generator, seed=seed)

    terminals = [123, 230, 310, 464, 588, 625, 700]

    kr = KleinRavi(node_weighted, terminals)
    kr_st = kr.steiner_tree()
    kr_cost, node_cost = kr_st.compute_total_weights(terminals)

    ngh = NetworkXGraphHelper(node_weighted)
    ngh.draw_graph(special_nodes=[(terminals, "#0000FF", None)],
                   title_1="Klein-Ravi's algorithm (node-weighted network graph), seed = " + str(seed),
                   title_2="Cost: "+str(kr_cost)+", Nodes: "+str(node_cost)+", Edges: "+str(kr_cost - node_cost),
                   print_node_labels=False)
