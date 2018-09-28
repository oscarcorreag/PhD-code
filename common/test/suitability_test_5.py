from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus import Dreyfus


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 30

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    for _, (r, _, _, _, _, _) in regions.iteritems():
        df = Dreyfus(r)
        print("region:", r)
        for v in r:
            ecc, inc = r.steiner_n_stats(3, v, df)
            print(v, ecc, inc)

    ngh = NetworkXGraphHelper(node_weighted)
    ngh.draw_graph(node_weight_generator=generator,
                   print_node_labels=True,
                   node_size=15,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()])
