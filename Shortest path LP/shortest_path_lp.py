from scipy.optimize import linprog


def shortest_path_primal(graph, start):

    node_weighted = graph.is_node_weighted()

    variables = set()
    constraints = []
    b_eq = []
    cost_coeff_dict = {}
    for v in graph:
        if not node_weighted:
            adj_nodes = graph[v]
        else:
            adj_nodes = graph[v][1]
        constraint = {}
        for w, dist in adj_nodes.iteritems():
            var1 = (v, w)
            var2 = (w, v)
            variables.add(var1)
            variables.add(var2)
            cost_coeff_dict[var1] = dist
            constraint[var1] = -1
            constraint[var2] = 1
        constraints.append(constraint)
        b = 1
        if v == start:
            b = -(len(graph.keys()) - 1)
        b_eq.append(b)

    c = []
    A_eq = []
    vars_list = list(variables)
    for variable in vars_list:
        c.append(cost_coeff_dict[variable])
    for constraint in constraints:
        cons = []
        for variable in vars_list:
            if variable in constraint:
                cons.append(constraint[variable])
            else:
                cons.append(0)
        A_eq.append(cons)

    res = linprog(c=c, A_eq=A_eq, b_eq=b_eq, options={"maxiter": 10000})
    print(res)
    predecessors = build_predecessors(vars_list, res['x'])

    return build_distances_paths(graph, predecessors, start)


def shortest_path_dual(graph, start):

    node_weighted = graph.is_node_weighted()

    c = []
    vars_list = []
    constraints = []
    b_ub = []
    bounds = []
    for v in graph:
        if v == start:
            c.append(len(graph.keys()) - 1)
            bounds.append((0, None))
        else:
            c.append(-1)
            bounds.append((None, None))
        vars_list.append(v)
        if not node_weighted:
            adj_nodes = graph[v]
        else:
            adj_nodes = graph[v][1]
        for w, dist in adj_nodes.iteritems():
            constraint = {v: -1, w: 1}
            constraints.append(constraint)
            b_ub.append(dist)

    A_ub = []
    for constraint in constraints:
        cons = []
        for variable in vars_list:
            if variable in constraint:
                cons.append(constraint[variable])
            else:
                cons.append(0)
        A_ub.append(cons)

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, options={"maxiter": 10000})
    print(res)

    return build_distances(vars_list, res['x'])


def build_predecessors(vars_list, x_results):
    predecessors = {}
    for i in range(len(vars_list)):
        if x_results[i] != 0.:
            predecessors[vars_list[i][1]] = vars_list[i][0]
    return predecessors


def build_distances_paths(graph, predecessors, start):

    node_weighted = graph.is_node_weighted()

    distances = {}
    paths = {}
    for v in graph:
        distance = 0
        path = []
        w = v
        while 1:
            path.append(w)
            if w == start:
                break
            if not node_weighted:
                distance += graph[w][predecessors[w]]
            else:
                distance += graph[w][1][predecessors[w]]
            w = predecessors[w]
        distances[v] = distance
        path.reverse()
        paths[v] = path
    return distances, paths


def build_distances(vars_list, x_results):
    distances = {}
    for i in range(len(vars_list)):
        distances[vars_list[i]] = x_results[i]
    return distances
