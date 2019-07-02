from spiders import Spiders
from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 1
    m = n = 80

    # node_weights = [generator.weights['WARNING'][0] for _ in range(m * n)]
    # node_weights[770] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[720] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[721] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[771] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[722] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[772] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[2333] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[2383] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1573] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1574] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1623] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1624] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1120] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[931] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[930] = generator.weights['VERY_SUITABLE'][0]

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n,
                        edge_weighted=True,
                        node_weighted=True,
                        node_weight_generator=generator,
                        # node_weights=node_weights,
                        seed=seed)

    # terminals = [1265, 1134, 1482, 1721, 677, 1567, 814, 1879, 635, 838, 2077, 2227, 911]
    # poi = 1226

    # terminals = [470, 388, 750, 1185, 1222, 739, 487, 850, 1299, 333]
    # poi = 899

    # terminals = [858, 703, 171, 628, 886, 240, 383, 268, 686]
    # poi = 668
    terminals = [2580, 2655, 3622, 2161, 5247, 5073, 871, 4946, 1017]
    poi = 3381

    # terminals = [331, 356, 297]
    # poi = 294

    # terminals = [197, 221]
    # poi = 74

    # terminals = [123, 230, 310, 588, 625, 700]
    # poi = 464

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    c = Spiders(suitability_graph, terminals, poi)
    c_st, meeting_nodes = c.steiner_tree()

    term_poi = [t for t in terminals]
    term_poi.append(poi)
    cost, node_cost = c_st.compute_total_weights(term_poi)

    # legend = [str(counter + 1) + ". imp->" + str(mn[0]) + " for: " + str(mn[1]) for counter, mn in
    #           enumerate(meeting_nodes)]

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=terminals,
                   nodes_2=[poi],
                   subgraphs_1=[r for _, (r, _, _) in regions.iteritems()],
                   subgraphs_2=[c_st],
                   node_weight_generator=generator,
                   title_1="Spiders, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", Nodes: " + str(node_cost) + ", Edges: " + str(cost - node_cost),
                   # legend=legend,
                   print_node_labels=False,
                   node_size=15)
