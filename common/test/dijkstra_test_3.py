from grid_digraph_generator import GridDigraphGenerator


if __name__ == '__main__':
    m = n = 40
    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)
    graph.compute_dist_paths(origins=[0], destinations=[20, 21], end_mode='all', track_edges=True)
    print graph.dist
    print graph.paths
    weights = {(0, 1): 2}
    graph.update_edge_weights(weights)

