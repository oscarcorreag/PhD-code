from grid_digraph_generator import GridDigraphGenerator
from rayward_smith import RaywardSmith
from networkx_graph_helper import NetworkXGraphHelper

if __name__ == '__main__':

    gh = GridDigraphGenerator()
    graph = gh.generate(30, 30, edge_weighted=False)
    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 469, 186]
    # terminals = [3, 7, 9, 15]

    rs = RaywardSmith(graph, terminals)
    # steiner_tree, cost, best_nodes = rs.steiner_tree()
    rs_st = rs.steiner_tree()
    rs_cost, node_cost = rs_st.calculate_costs(terminals)

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(terminals, None, None)],
                   special_subgraphs=[(rs_st, None)],
                   title_1='Rayward-Smith algorithm (network graph)',
                   title_2="Cost: "+str(rs_cost)+", Nodes: "+str(node_cost)+", Edges: "+str(rs_cost - node_cost),
                   print_node_labels=False)
