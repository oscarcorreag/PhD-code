import operator
from scipy.optimize import linprog
from digraph import Digraph


class SteinerForestLPDirected:

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
        # Create the edge orientation constraints.
        A_ub_d = {}
        for e, _ in E.iteritems():
            for ts in self.__terminals:
                ts_ = set(ts)
                for v in ts:
                    ws = ts_.difference([v])
                    for w in ws:
                        # First inequality.
                        try:
                            A_ub_d[(e, v, w, 0)][(e[0], e[1], v)] = -1
                        except KeyError:
                            A_ub_d[(e, v, w, 0)] = {(e[0], e[1], v): -1}
                        A_ub_d[(e, v, w, 0)][(e[1], e[0], w)] = -1
                        # Second inequality.
                        try:
                            A_ub_d[(e, v, w, 1)][e] = -1
                        except KeyError:
                            A_ub_d[(e, v, w, 1)] = {e: -1}
                        A_ub_d[(e, v, w, 1)][(e[0], e[1], v)] = 1
                        A_ub_d[(e, v, w, 1)][(e[1], e[0], w)] = 1
        A_ub = []
        b_ub = []
        for e in E:
            for ts in self.__terminals:
                ts_ = set(ts)
                for v in ts:
                    ws = ts_.difference([v])
                    for w in ws:
                        a0 = []
                        a1 = []
                        for var, _ in sorted_vars:
                            if var in A_ub_d[(e, v, w, 0)]:
                                a0.append(A_ub_d[(e, v, w, 0)][var])
                            else:
                                a0.append(0)
                            if var in A_ub_d[(e, v, w, 1)]:
                                a1.append(A_ub_d[(e, v, w, 1)][var])
                            else:
                                a1.append(0)
                        A_ub.append(a0)
                        A_ub.append(a1)
                        b_ub.append(0)
                        b_ub.append(0)
        # print A_ub
        # Solve the linear program.
        res = linprog(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, options={"maxiter": 1000000})
        print res
        # Build the Steiner forest.
        steiner_forest = Digraph()
        for i in range(len(res['x'])):
            if res['x'][i] > .4:
                if len(sorted_vars[i][0]) == 2:
                    steiner_forest.append_edge_1(sorted_vars[i][0], self.__graph)

        return steiner_forest
