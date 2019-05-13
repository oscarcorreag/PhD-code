from grid_digraph_generator import GridDigraphGenerator
from digraph import Digraph


if __name__ == '__main__':
    # Meet-in-the-middle shortest path
    # Grid digraph
    m = n = 40
    gh = GridDigraphGenerator()
    graph_1 = gh.generate(m, n, edge_weighted=False)
    graph_1.compute_dist_paths([5], [399], method='meet-in-the-middle')
    # Custom digraph
    graph_2 = Digraph()
    graph_2.append_edge_2((0, 1), weight=1)
    graph_2.append_edge_2((1, 2), weight=1)
    graph_2.append_edge_2((2, 3), weight=5)
    graph_2.append_edge_2((3, 4), weight=1)
    graph_2.append_edge_2((2, 5), weight=2)
    graph_2.append_edge_2((5, 6), weight=2)
    graph_2.append_edge_2((6, 3), weight=2)
    graph_2.compute_dist_paths([0], [4], method='meet-in-the-middle')

    # Explore graph from starting node
    distances = graph_2.explore_upto(2, 1)
    print distances