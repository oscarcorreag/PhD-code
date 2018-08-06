from grid_digraph_generator import GridDigraphGenerator


if __name__ == '__main__':
    m = n = 40
    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)
    graph.compute_dist_paths(origins=[0], destinations=[21], track_edges=True)
    print graph.dist
    print graph.paths
    weights = {(0, 1): 4}
    graph.update_edge_weights(weights)
    print graph.dist
    print graph.paths
