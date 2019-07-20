import numpy as np
import time
import csv
import sys

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from statistics import get_statistics

from vst_rs import VST_RS
from voronoi_based import VoronoiBased
from hotspot_based import HotspotBased

if __name__ == '__main__':

    seeds = [0, 1, 2, 3, 4]
    # num_samples = 10
    num_samples = 10
    # sizes = [60, 70, 80]
    ms = [100]
    ns = [100]
    # nums_terminals = [60, 65, 70]
    nums_terminals = [256]
    # nums_pois = [5, 6, 7, 8, 9, 10]
    nums_pois = [80]
    # num_extensions = 1
    capacity = [4]
    results = []

    generator = SuitableNodeWeightGenerator()

    # try:
    for seed in seeds:
        print("seed:", seed)
        for msns in range(len(ms)):
            print("nodes:", ms[msns] * ns[msns])
            graph = GridDigraphGenerator().generate(ms[msns], ns[msns],
                                                    node_weighted=True,
                                                    node_weight_generator=generator,
                                                    seed=seed)
            suitability_graph = SuitabilityGraph()
            suitability_graph.append_graph(graph)
            hotspots = suitability_graph.get_suitable_nodes(generator)

            start_time = time.clock()
            suitability_graph.compute_dist_paths(origins=hotspots, destinations=hotspots, compute_paths=False)
            print "compute", time.clock() - start_time, "# hotspots:", len(hotspots)

            for num_seats in capacity:
                # suitability_graph.extend_suitable_regions(seed, generator)
                # hotspots = suitability_graph.get_suitable_nodes(generator)
                # print i, "# hotspots:", len(hotspots)
                for num_terminals in nums_terminals:
                    new_terminals = set()
                    for sample in range(num_samples):
                        graph_temp = SuitabilityGraph()
                        graph_temp.append_graph(suitability_graph)
                        graph_temp.dist = dict(suitability_graph.dist)
                        graph_temp.pairs_dist_paths = set(suitability_graph.pairs_dist_paths)
                        graph_temp.method_dist_paths = suitability_graph.method_dist_paths
                        print("sample:", sample)
                        terminals = np.random.choice(a=ms[msns] * ns[msns], size=num_terminals + max(nums_pois),
                                                     replace=False)
                        # while len(set(hotspots).intersection(terminals)) != 0:
                        #     terminals = np.random.choice(a=size * size, size=num_terminals + max(nums_pois), replace=False)
                        temp = set(hotspots)
                        temp.update(terminals)
                        start_time = time.clock()
                        graph_temp.update_dist_paths(temp, compute_paths=False)
                        print "update", time.clock() - start_time
                        num_hotspots = len(set(hotspots).difference(terminals))
                        print "# hotspots:", num_hotspots
                        for num_pois in nums_pois:
                            ind_pois = np.random.choice(a=num_terminals + max(nums_pois), size=num_pois, replace=False)
                            pois = [terminals[ind] for ind in ind_pois]
                            terminals_ = list(set(terminals).difference(pois))
                            # pois = np.random.choice(a=size * size, size=num_pois, replace=False)
                            # while len(set(hotspots).intersection(pois)) != 0 \
                            #         or len(set(terminals).intersection(pois)) != 0:
                            #     pois = np.random.choice(a=size * size, size=num_pois, replace=False)
                            # print(pois, ";", terminals_)
                            # ----------
                            # Mustafiz
                            # ----------
                            mz = VST_RS(graph_temp, terminals_, pois, num_seats, 10)
                            try:
                                start_time = time.clock()
                                forest, cost, gr, avg_dr, num_cars, avg_or = mz.steiner_forest()
                                elapsed_time = time.clock() - start_time
                                # cost2, _ = forest.calculate_costs()
                                line = ["mVST-RS", seed, ms[msns] * ns[msns], num_hotspots, num_terminals, num_pois,
                                        num_seats, sample + 1,
                                        elapsed_time, cost, gr, avg_dr, num_cars, avg_or]
                            except ValueError:
                                line = ["mVST-RS", seed, ms[msns] * ns[msns], num_hotspots, num_terminals, num_pois,
                                        num_seats, sample + 1,
                                        "NA", "NA", "NA", "NA", "NA", "NA"]
                            results.append(line)
                            print line
                            # -------------------
                            # Hotspots K = 5 AND CLONE_HOTSPOTS = FALSE
                            # -------------------
                            hb = HotspotBased(graph_temp, terminals_, pois)
                            start_time = time.clock()
                            forest, cost, gr, avg_dr, num_cars, avg_or = hb.steiner_forest(k=num_seats, get_lsv=False)
                            elapsed_time = time.clock() - start_time
                            # cost2, _ = forest.calculate_costs()
                            line = ["Gr-based", seed, ms[msns] * ns[msns], num_hotspots, num_terminals, num_pois,
                                    num_seats, sample + 1,
                                    elapsed_time, cost, gr, avg_dr, num_cars, avg_or]
                            results.append(line)
                            print line
                            # # -------------------
                            # # Hotspots
                            # # -------------------
                            # hb = HotspotBased(graph_temp, terminals_, pois)
                            # start_time = time.clock()
                            # forest, cost, gr = hb.steiner_forest()
                            # elapsed_time = time.clock() - start_time
                            # # cost2, _ = forest.calculate_costs()
                            # line = ["Hot-spots", seed, ms[msns] * ns[msns], num_hotspots, num_terminals, num_pois, sample + 1,
                            #         elapsed_time, cost, gr]
                            # results.append(line)
                            # print line
                            # except:
    # print("Unexpected error:", sys.exc_info()[0], sys.exc_info()[1])

    result_file = open("files/experiments_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
