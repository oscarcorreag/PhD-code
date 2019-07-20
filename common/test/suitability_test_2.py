from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityGraph
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 40

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=False,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [0, 90]
    poi = 55

    terminals_poi = list(terminals)
    terminals_poi.append(poi)

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)
    exclusive = suitability_graph.build_suitability_metric_closure(generator, terminals_poi)

    ngh = NetworkXGraphHelper(exclusive)
    ngh.draw_graph(print_node_labels=True)
