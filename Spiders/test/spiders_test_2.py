import numpy as np

from spiders import Spiders
from suitability import OsmGraphManager, SuitableNodeWeightGenerator

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    gh = OsmGraphManager("postgres", "anabelle1803!", "osm")
    suitability_graph = gh.generate_based_on_coords(-37.779007, 144.927753, -37.835427, 144.983372, generator)

    indices = np.random.choice(a=len(suitability_graph.keys()), size=6, replace=False)
    terminals = [suitability_graph.keys()[i] for i in indices]

    s = Spiders(suitability_graph, terminals[1:], terminals[0], contract_graph=False)
    s_st, meeting_nodes = s.steiner_tree()

    cost, node_cost = s_st.compute_total_weights(terminals)

    print(cost, node_cost)
