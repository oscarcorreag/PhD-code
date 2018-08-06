import numpy as np

from dreyfus_imr import DreyfusIMR
from suitability import OsmGraphManager, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    seed = 0

    generator = SuitableNodeWeightGenerator()

    gh = OsmGraphManager("postgres", "anabelle1803!", "osm")
    suitability_graph = gh.generate_based_on_coords(-37.77722770873696, 144.90966796875, -37.84449479883458, 145.03463745117188, generator)

    np.random.seed(seed)

    indices = np.random.choice(a=len(suitability_graph.keys()), size=6, replace=False)
    terminals = [suitability_graph.keys()[i] for i in indices]

    print(terminals)

    contract_graph = False
    within_convex_hull = False
    consider_terminals = False

    dr = DreyfusIMR(suitability_graph, terminals, contract_graph=contract_graph, within_convex_hull=within_convex_hull)
    steiner_tree = dr.steiner_tree(consider_terminals=consider_terminals)

    cost, node_cost = steiner_tree.calculate_costs(terminals)

    print(steiner_tree)
    print(cost, node_cost)

    ngh = NetworkXGraphHelper(steiner_tree)
    ngh.draw_graph(node_weight_generator=generator, node_size=15)