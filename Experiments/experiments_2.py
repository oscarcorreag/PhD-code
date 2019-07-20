import numpy as np
import time
import csv
import sys

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from dijkstra import dijkstra
from spiders import Spiders
from gravitation import Gravitation
from dreyfus_imr import DreyfusIMR
from statistics import get_statistics

if __name__ == '__main__':

    seeds = range(5)
    num_samples = 10
    sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    nums_terminals = [6, 7, 8, 9, 10]

    generator = SuitableNodeWeightGenerator()

    results = []

    try:

        for seed in seeds:

            print("seed:", seed)

            for size in sizes:

                print("nodes:", size * size)

                graph = GridDigraphGenerator().generate(size,
                                                        size,
                                                        node_weighted=True,
                                                        node_weight_generator=generator,
                                                        seed=seed)

                suitability_graph = SuitabilityGraph()
                suitability_graph.append_graph(graph)

                suitability_graph.extend_suitable_regions(seed, generator)
                suitability_graph.extend_suitable_regions(seed, generator)

                total_num_suitable_nodes = len(suitability_graph.get_suitable_nodes(generator))

                # start_time = time.clock()
                # suitable_nodes = suitability_graph.get_suitable_nodes(generator)
                # dist_paths = {n: dijkstra(suitability_graph, n, consider_node_weights=False) for n in suitable_nodes}
                # dijkstra_time = time.clock() - start_time

                start_time = time.clock()
                suitability_graph.contract_suitable_regions(generator)
                suitable_nodes_contracted_graph = suitability_graph.get_suitable_nodes(generator)
                dist_paths_contracted_graph = {n: dijkstra(suitability_graph, n, consider_node_weights=False)
                                               for n in suitable_nodes_contracted_graph}
                dijkstra_time_contracted_graph = time.clock() - start_time

                # total_num_nodes = len(suitability_graph.keys())

                for num_terminals in nums_terminals:

                    for sample in range(num_samples):

                        print("sample:", sample)

                        terminals = np.random.choice(a=size * size, size=num_terminals, replace=False)
                        while set(suitability_graph.keys()).intersection(terminals) != set(terminals) \
                                or set(suitable_nodes_contracted_graph).intersection(terminals) != set():
                            terminals = np.random.choice(a=size * size, size=num_terminals, replace=False)
                        poi = terminals[0]

                        # Spiders
                        start_time = time.clock()
                        alg = Spiders(graph=graph, terminals=terminals[1:], poi=poi, contracted_graph=suitability_graph,
                                      dist_paths_suitable_nodes=dist_paths_contracted_graph)
                        steiner_tree, _ = alg.steiner_tree()

                        cost, node_cost, num_suitable_nodes, num_steiner_nodes, num_leaves = \
                            get_statistics(steiner_tree, terminals, generator)

                        line = ["Spiders", seed, size * size, total_num_suitable_nodes, num_terminals,
                                dijkstra_time_contracted_graph, sample + 1, time.clock() - start_time, cost - node_cost,
                                num_suitable_nodes, num_steiner_nodes, num_leaves]
                        line.extend(terminals)
                        results.append(line)

                        # Dreyfus algorithm IMR
                        start_time = time.clock()
                        # alg = DreyfusIMR(graph, terminals, dist_paths)
                        alg = DreyfusIMR(graph=graph, terminals=terminals, contracted_graph=suitability_graph,
                                         dist_paths_nodes=dist_paths_contracted_graph)
                        steiner_tree = alg.steiner_tree()

                        cost, node_cost, num_suitable_nodes, num_steiner_nodes, num_leaves = \
                            get_statistics(steiner_tree, terminals, generator)

                        # line = ["Dreyfus", seed, size * size, total_num_suitable_nodes, num_terminals, dijkstra_time,
                        #         sample + 1, time.clock() - start_time, cost - node_cost, num_suitable_nodes,
                        #         num_steiner_nodes, num_leaves]
                        line = ["Dreyfus", seed, size * size, total_num_suitable_nodes, num_terminals,
                                dijkstra_time_contracted_graph, sample + 1, time.clock() - start_time, cost - node_cost,
                                num_suitable_nodes, num_steiner_nodes, num_leaves]
                        line.extend(terminals)
                        results.append(line)

                        # Gravitation algorithm: max_level_attraction=2
                        start_time = time.clock()
                        alg = Gravitation(graph=graph, terminals=terminals[1:], poi=poi, max_level_attraction=2,
                                          contracted_graph=suitability_graph,
                                          dist_paths_suitable_nodes=dist_paths_contracted_graph)
                        steiner_tree = alg.steiner_tree()

                        cost, node_cost, num_suitable_nodes, num_steiner_nodes, num_leaves = \
                            get_statistics(steiner_tree, terminals, generator)

                        line = ["Gravitation 2", seed, size * size, total_num_suitable_nodes, num_terminals,
                                dijkstra_time_contracted_graph, sample + 1, time.clock() - start_time, cost - node_cost,
                                num_suitable_nodes, num_steiner_nodes, num_leaves]
                        line.extend(terminals)
                        results.append(line)

                        # Gravitation algorithm: max_level_attraction=3
                        start_time = time.clock()
                        alg = Gravitation(graph=graph, terminals=terminals[1:], poi=poi, max_level_attraction=3,
                                          contracted_graph=suitability_graph,
                                          dist_paths_suitable_nodes=dist_paths_contracted_graph)
                        steiner_tree = alg.steiner_tree()

                        cost, node_cost, num_suitable_nodes, num_steiner_nodes, num_leaves = \
                            get_statistics(steiner_tree, terminals, generator)

                        line = ["Gravitation 3", seed, size * size, total_num_suitable_nodes, num_terminals,
                                dijkstra_time_contracted_graph, sample + 1, time.clock() - start_time, cost - node_cost,
                                num_suitable_nodes, num_steiner_nodes, num_leaves]
                        line.extend(terminals)
                        results.append(line)

    except:
        print("Unexpected error:", sys.exc_info()[0], sys.exc_info()[1])

    result_file = open("files/experiments_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
