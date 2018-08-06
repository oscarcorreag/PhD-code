import numpy as np
import time

from lazy_steiner_tree import LazySteinerTree
from suitability import OsmGraphManager, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    seed = 0

    generator = SuitableNodeWeightGenerator()

    gh = OsmGraphManager("postgres", "anabelle1803!", "osm")
    # suitability_graph = gh.generate(-37.7772277087369, 144.9096679687, -37.8444947988345, 145.0346374511718, generator)
    suitability_graph = gh.generate_based_on_coords(-37.748186293725915, 144.93541717529297, -37.797305754993076, 144.9949836730957, generator)

    np.random.seed(seed)

    indices = np.random.choice(a=len(suitability_graph.keys()), size=6, replace=False)
    terminals = [suitability_graph.keys()[i] for i in indices]

    print(terminals)

    lst = LazySteinerTree(suitability_graph, terminals, generator=generator)

    start_time = time.clock()
    steiner_tree = lst.steiner_tree()
    print("elapsed time:", time.clock() - start_time)
