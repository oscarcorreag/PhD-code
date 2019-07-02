import numpy as np
import time
import csv

import sys

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from spiders import Spiders
from dreyfus_imr import DreyfusIMR
from utils import id_generator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    num_seeds = 1
    num_samples = 3
    sizes = [90]
    nums_terminals = [7]

    generator = SuitableNodeWeightGenerator()

    results = []

    try:

        for seed in range(num_seeds):
            for size in sizes:
                graph = GridDigraphGenerator().generate(size,
                                                        size,
                                                        node_weighted=True,
                                                        node_weight_generator=generator,
                                                        seed=seed)

                suitability_graph = SuitabilityDigraph()
                suitability_graph.append_from_graph(graph)

                total_num_suitable_nodes = len(suitability_graph.get_suitable_nodes(generator))

                for num_terminals in nums_terminals:

                    for sample in range(num_samples):

                        line = [seed, size * size, total_num_suitable_nodes, num_terminals, sample + 1]

                        terminals = np.random.choice(a=size * size, size=num_terminals, replace=False)
                        poi = terminals[0]

                        # Spiders
                        start_time = time.clock()
                        alg = Spiders(suitability_graph, terminals[1:], poi)
                        steiner_tree, _ = alg.steiner_tree()
                        line.append(time.clock() - start_time)

                        cost, node_cost = steiner_tree.compute_total_weights(terminals)
                        line.append(cost - node_cost)

                        steiner_tree.__class__ = SuitabilityDigraph
                        line.append(len(steiner_tree.get_suitable_nodes(generator,
                                                                        excluded_nodes=terminals)))
                        line.append(len(steiner_tree.get_suitable_nodes(generator,
                                                                        degree_more_than=2,
                                                                        excluded_nodes=terminals)))
                        line.append(len(steiner_tree.get_suitable_nodes(generator,
                                                                        degree_equals_to=1,
                                                                        excluded_nodes=terminals)))

                        # # Dreyfus algorithm IMR
                        # start_time = time.clock()
                        # alg = DreyfusIMR(suitability_graph, terminals)
                        # steiner_tree, cost = alg.steiner_tree()
                        # line.append(time.clock() - start_time)
                        #
                        # line.append(cost)
                        #
                        # steiner_tree.__class__ = SuitabilityDigraph
                        # line.append(len(steiner_tree.get_suitable_nodes(generator,
                        #                                                 excluded_nodes=terminals)))
                        # line.append(len(steiner_tree.get_suitable_nodes(generator,
                        #                                                 degree_more_than=2,
                        #                                                 excluded_nodes=terminals)))
                        # line.append(len(steiner_tree.get_suitable_nodes(generator,
                        #                                                 degree_equals_to=1,
                        #                                                 excluded_nodes=terminals)))

                        # ngh = NetworkXGraphHelper(graph)
                        # ngh.draw_graph(nodes_2=terminals,
                        #                subgraphs_2=[steiner_tree],
                        #                node_weight_generator=generator,
                        #                title_1="Dreyfus IMR algorithm (network graph), seed = " + str(seed),
                        #                title_2="Cost: " + str(cost),
                        #                node_labels=False)

                        list_terminals = [t for t in terminals]
                        for i in range(10 - num_terminals):
                            list_terminals.append(0)

                        line.extend(list_terminals)
                        print(line)
                        results.append(line)
    except:
        print("Unexpected error:", sys.exc_info()[0], sys.exc_info()[1])

    result_file = open("files/experiments_" + id_generator() + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
