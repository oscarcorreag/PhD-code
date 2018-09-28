import time

from baltz import Baltz
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False, node_weighted=True, node_weight_generator=generator)

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)

    weights = {v: generator.weights["VERY_SUITABLE"][0] for v in suitability_graph}
    suitability_graph.update_node_weights(weights)

    b = Baltz(suitability_graph)

    requests = [[27, 22, 55, 43], [35, 63, 76], [42, 47, 68], [56, 64, 23], [33, 25, 75]]
    st = time.clock()
    MSTs = b.steiner_forest(requests)
    et = time.clock() - st

    print et

    special_subgraphs = [(MST, None) for _, (MST, cost) in MSTs.iteritems()]

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_subgraphs=special_subgraphs, print_node_labels=True)

    # mz = Mustafiz(suitability_graph, [63, 76], [35], 4, sys.maxint)
    # T0, l, _, _, _, _ = mz.steiner_forest()
    # special_subgraphs = [(T0, '#000000')]
    # ngh = NetworkXGraphHelper(suitability_graph)
    # ngh.draw_graph(special_subgraphs=special_subgraphs, node_labels=True)
    #
    # mz = Mustafiz(suitability_graph, [47, 68], [42], 4, sys.maxint)
    # T1, l, _, _, _, _ = mz.steiner_forest()
    # special_subgraphs = [(T1, '#0000FF')]
    # ngh = NetworkXGraphHelper(suitability_graph)
    # ngh.draw_graph(special_subgraphs=special_subgraphs, node_labels=True)
    #
    # mz = Mustafiz(suitability_graph, [64, 23], [56], 4, sys.maxint)
    # T2, l, _, _, _, _ = mz.steiner_forest()
    # special_subgraphs = [(T2, '#13E853')]
    # ngh = NetworkXGraphHelper(suitability_graph)
    # ngh.draw_graph(special_subgraphs=special_subgraphs, node_labels=True)
    #
    # mz = Mustafiz(suitability_graph, [25, 75], [33], 4, sys.maxint)
    # T3, l, _, _, _, _ = mz.steiner_forest()
    # special_subgraphs = [(T3, '#FF0000')]
    # ngh = NetworkXGraphHelper(suitability_graph)
    # ngh.draw_graph(special_subgraphs=special_subgraphs, node_labels=True)
