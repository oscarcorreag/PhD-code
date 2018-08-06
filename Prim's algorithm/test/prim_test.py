from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from prim import Prim


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 10

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=False,
                                # node_weight_generator=generator,
                                seed=seed)

    p = Prim(node_weighted)
    spanning_tree = p.spanning_tree()

    cost, node_cost = spanning_tree.calculate_costs()

    ngh = NetworkXGraphHelper(node_weighted)
    ngh.draw_graph(subgraphs_2=[spanning_tree],
                   node_weight_generator=generator,
                   title_1="Prim's algorithm, seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost),
                   print_node_labels=False,
                   node_size=15)
