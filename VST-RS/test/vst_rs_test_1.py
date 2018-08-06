import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from vst_rs import VST_RS


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 1
    m = n = 30

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, capacitated=True, capacities_range=(1, 100),
                        edge_weighted=False,
                        node_weighted=True,
                        node_weight_generator=generator,
                        seed=seed)

    terminals = np.random.choice(a=m * n, size=50, replace=False)
    pois = terminals[:5]
    terminals = terminals[5:]

    mz = VST_RS(graph)
    start_time = time.clock()
    forest, cost, _, _, _, _, sts = mz.steiner_forest(terminals, pois, 4, 8)
    elapsed_time = time.clock() - start_time

    special_nodes = [(terminals, '#000000', 35), (pois, '#0000FF', 65)]

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=special_nodes,
                   # special_subgraphs=[(forest, "#FF0000")],
                   special_subgraphs=[(st, None) for st in sts],
                   title_1="Mustafiz's algorithm, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", elapsed time: " + str(elapsed_time))
