
def get_statistics(steiner_tree, terminals, generator):

    cost, node_cost = steiner_tree.compute_total_weights(terminals)
    num_suitable_nodes = len(steiner_tree.get_suitable_nodes(generator, excluded_nodes=terminals))
    num_steiner_nodes = len(steiner_tree.get_suitable_nodes(generator, degree_more_than=2, excluded_nodes=terminals))
    num_leaves = len(steiner_tree.get_suitable_nodes(generator, degree_equals_to=1, excluded_nodes=terminals))

    return cost, node_cost, num_suitable_nodes, num_steiner_nodes, num_leaves
