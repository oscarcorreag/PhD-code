import operator
from scipy.optimize import linprog
from graph import Graph


class SteinerForestLP:

    def __init__(self, graph, requests):
        self.__graph = graph
        self.__terminals = [r[1:] for r in requests]
        self.__roots = [r[0] for r in requests]

    def steiner_forest(self):
        vars_ = {}  # Dictionary of variables.
        E = self.__graph.get_edges()
        # Allocate x_ij variables.
        for i, e in enumerate(E):
            vars_[e] = i
        # Allocate f_k_ij variables (both directions).
        i = len(vars_)
        for e in E:
            for ts in self.__terminals:
                for t in ts:
                    vars_[(e[0], e[1], t)] = i
                    i += 1
                    vars_[(e[1], e[0], t)] = i
                    i += 1
        # Sort dictionary of variables by index.
        sorted_vars = sorted(vars_.iteritems(), key=operator.itemgetter(1))
        # Create the c vector.
        c = []
        for var, _ in sorted_vars:
            try:
                c.append(E[var])
            except KeyError:
                c.append(0)
        # Create the conservation of flow constraints.
        A_eq_d = {}
        b_eq_d = {}
        for v, val in self.__graph.iteritems():
            for w, _ in val.iteritems():
                for ts in self.__terminals:
                    for t in ts:
                        try:
                            A_eq_d[(v, t)][(v, w, t)] = 1
                        except KeyError:
                            A_eq_d[(v, t)] = {(v, w, t): 1}
                        try:
                            A_eq_d[(v, t)][(w, v, t)] = -1
                        except KeyError:
                            A_eq_d[(v, t)] = {(w, v, t): -1}
            for k, ts in enumerate(self.__terminals):
                for t in ts:
                    if v == self.__roots[k]:
                        b_eq_d[(v, t)] = 1
                    elif v == t:
                        b_eq_d[(v, t)] = -1
                    else:
                        b_eq_d[(v, t)] = 0
        A_eq = []
        b_eq = []
        for v in self.__graph:
            for ts in self.__terminals:
                for t in ts:
                    a = []
                    for var, _ in sorted_vars:
                        if var in A_eq_d[(v, t)]:
                            a.append(A_eq_d[(v, t)][var])
                        else:
                            a.append(0)
                    A_eq.append(a)
                    b_eq.append(b_eq_d[(v, t)])
        # Create "capacity" constraints.
        A_ub_d = {}
        for e, _ in E.iteritems():
            for ts in self.__terminals:
                for t in ts:
                    try:
                        A_ub_d[(e, t)][e] = -1
                    except KeyError:
                        A_ub_d[(e, t)] = {e: -1}
                    A_ub_d[(e, t)][(e[0], e[1], t)] = 1
                    A_ub_d[(e, t)][(e[1], e[0], t)] = 1
        A_ub = []
        b_ub = []
        for e in E:
            for ts in self.__terminals:
                for t in ts:
                    a = []
                    for var, _ in sorted_vars:
                        if var in A_ub_d[(e, t)]:
                            a.append(A_ub_d[(e, t)][var])
                        else:
                            a.append(0)
                    A_ub.append(a)
                    b_ub.append(0)
        # Solve the linear program.
        res = linprog(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, options={"maxiter": 1000000})
        print res
        # Build the Steiner forest.
        steiner_forest = Graph()
        for i in range(len(res['x'])):
            if res['x'][i] >= .499999:
                if len(sorted_vars[i][0]) == 2:
                    steiner_forest.append_edge_1(sorted_vars[i][0], self.__graph)

        return steiner_forest
