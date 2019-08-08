import operator
import sys

from graph import Graph
from ortools.linear_solver import pywraplp
from utils import id_generator
from itertools import product
from priodict import PriorityDictionary
from random import Random


def sample(nc, ng, min_s, max_s, nv, vertices, seed=None):
    rs, ss, cs = sample_requests(nc, ng, min_s, max_s, vertices, seed=seed)
    vertices_ = set(vertices).difference(set(ss.keys()).union(cs.keys()))
    vs = sample_vehicles(nv, vertices_, seed=seed)
    return rs, ss, cs, vs


def sample_requests(nc, ng, min_s, max_s, vertices, seed=None):
    #
    rnd = Random()
    if seed is not None:
        rnd = Random(seed)
    #
    groups = list()
    vertices_ = set(vertices)
    shops = dict()
    for g in range(ng):
        k = rnd.randint(min_s, max_s)
        ss = rnd.sample(vertices_, k)
        shops.update({s: g for s in ss})
        shops_tws = list()
        for shop in ss:
            earliest = rnd.randint(0, 23)
            latest = rnd.randint(earliest, 23)
            shops_tws.append((shop, earliest, latest))
        groups.append(shops_tws)
        vertices_ = vertices_.difference(ss)
    requests = list()
    customers = dict()
    for _ in range(nc):
        customer = rnd.choice(list(vertices_))
        earliest = rnd.randint(0, 23)
        latest = rnd.randint(earliest, 23)
        group_idx = rnd.randint(0, ng - 1)
        requests.append((groups[group_idx], (customer, earliest, latest)))
        customers[customer] = group_idx
        vertices_.remove(customer)
    return requests, shops, customers


def sample_vehicles(nv, vertices, seed=None):
    vertices_ = set(vertices)
    rnd = Random()
    if seed is not None:
        rnd = Random(seed)
    vehicles = list()
    for _ in range(nv):
        vehicle_s = rnd.choice(list(vertices_))
        vertices_.remove(vehicle_s)
        earliest_s = rnd.randint(0, 22)
        latest_s = rnd.randint(earliest_s, 22)
        vehicle_e = rnd.choice(list(vertices_))
        vertices_.remove(vehicle_e)
        earliest_e = rnd.randint(earliest_s + 1, 23)
        latest_e = rnd.randint(earliest_e, 23)
        vehicles.append(((vehicle_s, earliest_s, latest_s), (vehicle_e, earliest_e, latest_e)))
    return vehicles


def check_constraints(constraints):
    for c in constraints:
        if isinstance(c, int):
            raise (RuntimeError, "Constraint number estimation was wrong!")


class CsdpAp:
    def __init__(self, graph):
        # self._graph = Digraph(undirected=False)
        self._graph = Graph()
        self._graph.append_graph(graph)
        self._working_graph = None

        self._drivers = list()
        self._ad_hoc_drivers = list()
        self._dedicated_drivers = list()
        self._requests = list()
        # --------------------------------------------------------------------------------------------------------------
        # Arc subsets
        # --------------------------------------------------------------------------------------------------------------
        self.A1 = list()
        self.A2 = list()
        self.A3 = list()
        self.A4 = list()
        self.A5 = list()
        self.A6 = list()
        self.A7 = list()
        # --------------------------------------------------------------------------------------------------------------
        # Vertex subsets
        # --------------------------------------------------------------------------------------------------------------
        self._shops = set()
        self._customers = set()

        self._shops_dict = dict()
        self._customers_dict = dict()
        self._shops_by_group_id = dict()
        self._customers_by_group_id = dict()

        self.N = list()
        self.H_s = list()
        self.H_e = list()
        self.F_s = list()
        self.F_e = list()
        self._shop_by_F = dict()
        self._Fs_by_shop = dict()
        self.D = list()
        # self._V_tws = dict()  # All vertices each with its time window.
        # --------------------------------------------------------------------------------------------------------------
        # MILP
        # --------------------------------------------------------------------------------------------------------------
        self._solver = None
        self.x = dict()
        self.xs_by_driver = dict()
        self.B = dict()
        self.z = dict()
        self.w = dict()
        self.y = dict()

    def _define_arc_subsets(self):
        self.A1 = list()
        self.A2 = list()
        self.A3 = list()
        self.A4 = list()
        self.A5 = list()
        self.A6 = list()
        self.A7 = list()
        # Arc subset A1: From each vehicle start location to each pick-up location.
        for i in self.H_s:
            for j in self._shops:
                self.A1.append((i, j))
        for i in self.F_s:
            self.A1.append((i, self._shop_by_F[i]))
        # Arc subset A2: Between pick-up locations from different requests.
        for shop_1, group_id_1 in self._shops_dict.iteritems():
            for group_id_2, shops in self._shops_by_group_id.iteritems():
                if group_id_1 != group_id_2:
                    for shop_2 in shops:
                        self.A2.append((shop_1, shop_2))
        # Arc subset A3: From each pick-up location to each on-line customer location.
        for i in self._shops:
            for j in self._customers:
                self.A3.append((i, j))
        # Arc subset A4: From each on-line customer location to pick-up locations of a different request.
        for customer_1, group_id_1 in self._customers_dict.iteritems():
            for group_id_2, shops in self._shops_by_group_id.iteritems():
                if group_id_1 != group_id_2:
                    for shop_2 in shops:
                        self.A4.append((customer_1, shop_2))
        # Arc subset A5: Between on-line customer locations.
        for i in self._customers:
            for j in self._customers:
                if i != j:
                    self.A5.append((i, j))
        # Arc subset A6: From each on-line customer location to each vehicle end location.
        for i in self._customers:
            for j in self.H_e:
                self.A6.append((i, j))
        for customer, group_id in self._customers_dict.iteritems():
            for shop in self._shops_by_group_id[group_id]:
                _, end_v = self._Fs_by_shop[shop]
                self.A6.append((customer, end_v))
        # Arc subset A7: From a vehicle start location to the same-vehicle end location.
        for (i, _, _), (j, _, _) in self._drivers:
            self.A7.append((i, j))

    def _build_working_graph(self):
        self._working_graph = Graph(undirected=False)
        # Build arc sets.
        self._define_arc_subsets()
        # Build joint set of arcs and from it append edges to the working graph.
        A = list()
        A.extend(self.A1)
        A.extend(self.A2)
        A.extend(self.A3)
        A.extend(self.A4)
        A.extend(self.A5)
        A.extend(self.A6)
        A.extend(self.A7)
        # Shortest distances in the original graph are the weights of the arcs in the working graph.
        self._graph.compute_dist_paths(compute_paths=False)
        for i, j in A:
            self._working_graph.append_edge_2((i, j), weight=self._graph.dist[tuple(sorted([i, j]))])

    def _define_vars(self):
        self.x = dict()
        self.xs_by_driver = dict()
        self.B = dict()
        self.z = dict()
        self.w = dict()
        self.y = dict()
        # --------------------------------------------------------------------------------------------------------------
        # Boolean variables associated with combinations of arcs and vehicles.
        # --------------------------------------------------------------------------------------------------------------
        # These variables are defined over a subset of A1. Defining a x(i, j, k) for which i != k^+ does not make sense.
        for i, j in self.A1:
            for (s_v, _, _), (e_v, _, _) in self._drivers:
                if i == s_v:
                    self.x[(i, j, (s_v, e_v))] = self._solver.BoolVar("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v))
        # These variables are defined over A2 U A3 U A4 U A5 for ad hoc drivers.
        A_ = list()
        A_.extend(self.A2)
        A_.extend(self.A3)
        A_.extend(self.A4)
        A_.extend(self.A5)
        for i, j in A_:
            for s_v, e_v in self._ad_hoc_drivers:
                if self._solver.LookupVariable("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v)):
                    raise RuntimeError
                self.x[(i, j, (s_v, e_v))] = self._solver.BoolVar("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v))
        for i, j in self.A3:
            for s_v, e_v in self._dedicated_drivers:
                shop = self._shop_by_F[s_v]
                group_shop = self._shops_dict[shop]
                if i == shop and self._customers_dict[j] == group_shop:
                    if self._solver.LookupVariable("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v)):
                        raise RuntimeError
                    self.x[(i, j, (s_v, e_v))] = self._solver.BoolVar("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v))
        for i, j in self.A5:
            for s_v, e_v in self._dedicated_drivers:
                shop = self._shop_by_F[s_v]
                group_shop = self._shops_dict[shop]
                if self._customers_dict[i] == group_shop and self._customers_dict[j] == group_shop:
                    if self._solver.LookupVariable("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v)):
                        raise RuntimeError
                    self.x[(i, j, (s_v, e_v))] = self._solver.BoolVar("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v))
        # These variables are defined over a subset of A6. Defining a x(i, j, k) for which j != k^- does not make sense.
        for i, j in self.A6:
            for (s_v, _, _), (e_v, _, _) in self._drivers:
                if j == e_v:
                    if self._solver.LookupVariable("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v)):
                        raise RuntimeError
                    self.x[(i, j, (s_v, e_v))] = self._solver.BoolVar("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v))
        # These variables are defined over a subset of A7. Defining a x(i, j, k) for which i != k^+ or j != k^- does not
        # make sense. However, validating i and j is not needed as arcs {(i, j) : i = k^+ and j != k^-} are not created.
        for i, j in self.A7:
            for (s_v, _, _), (e_v, _, _) in self._drivers:
                if i == s_v and j == e_v:
                    if self._solver.LookupVariable("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v)):
                        raise RuntimeError
                    self.x[(i, j, (s_v, e_v))] = self._solver.BoolVar("x(%s, %s, (%s, %s))" % (i, j, s_v, e_v))
        # --------------------------------------------------------------------------------------------------------------
        # Time variables at which vehicles start servicing at vertices.
        # Time window constraints are defined implicitly.
        # --------------------------------------------------------------------------------------------------------------
        for i in self.N:
            # for (s_v, _, _), (e_v, _, _) in self._drivers:
            for s_v, e_v in self._ad_hoc_drivers:
                if self._solver.LookupVariable('B(%s, (%s, %s))' % (i, s_v, e_v)):
                    raise RuntimeError
                self.B[(i, (s_v, e_v))] = \
                    self._solver.NumVar(0.0, self._solver.infinity(), 'B(%s, (%s, %s))' % (i, s_v, e_v))
                # self.B[(i, k)] = self._solver.NumVar(self._V_tws[i][0], self._V_tws[i][1], 'B(%s, %s)' % (i, k))
        for s_v, e_v in self._dedicated_drivers:
            shop = self._shop_by_F[s_v]
            group_id = self._shops_dict[shop]
            if self._solver.LookupVariable('B(%s, (%s, %s))' % (shop, s_v, e_v)):
                raise RuntimeError
            self.B[(shop, (s_v, e_v))] = \
                self._solver.NumVar(0.0, self._solver.infinity(), 'B(%s, (%s, %s))' % (shop, s_v, e_v))
            for customer in self._customers_by_group_id[group_id]:
                if self._solver.LookupVariable('B(%s, (%s, %s))' % (customer, s_v, e_v)):
                    raise RuntimeError
                self.B[(customer, (s_v, e_v))] = \
                    self._solver.NumVar(0.0, self._solver.infinity(), 'B(%s, (%s, %s))' % (customer, s_v, e_v))

        for (s_v, _, _), (e_v, _, _) in self._drivers:
            if self._solver.LookupVariable('B(%s, (%s, %s))' % (s_v, s_v, e_v)):
                raise RuntimeError
            self.B[(s_v, (s_v, e_v))] = \
                self._solver.NumVar(0.0, self._solver.infinity(), 'B(%s, (%s, %s))' % (s_v, s_v, e_v))
            # self.B[(start_v, k)] = self._solver.NumVar(self._V_tws[start_v][0], self._V_tws[start_v][1],
            #                                            'B(%s, %s)' % (start_v, k))
            if self._solver.LookupVariable('B(%s, (%s, %s))' % (e_v, s_v, e_v)):
                raise RuntimeError
            self.B[(e_v, (s_v, e_v))] = \
                self._solver.NumVar(0.0, self._solver.infinity(), 'B(%s, (%s, %s))' % (e_v, s_v, e_v))
            # self.B[(end_v, k)] = self._solver.NumVar(self._V_tws[end_v][0], self._V_tws[end_v][1],
            #                                          'B(%s, %s)' % (end_v, k))
        # --------------------------------------------------------------------------------------------------------------
        # Auxiliary variables z(i, j, (s_v, e_v)) := x(i, j, (s_v, e_v)) * B(i, (s_v, e_v)).
        # --------------------------------------------------------------------------------------------------------------
        for i, j, (s_v, e_v) in self.x:
            self.z[(i, j, (s_v, e_v))] = \
                self._solver.NumVar(0.0, self._solver.infinity(), 'z(%s, %s, (%s, %s))' % (i, j, s_v, e_v))
            try:
                self.xs_by_driver[(s_v, e_v)].append((i, j, self.x[(i, j, (s_v, e_v))]))
            except KeyError:
                self.xs_by_driver[(s_v, e_v)] = [(i, j, self.x[(i, j, (s_v, e_v))])]

        for customer, group_id in self._customers_dict.iteritems():
            shops_customer = self._shops_by_group_id[group_id]
            # ----------------------------------------------------------------------------------------------------------
            # Auxiliary variables for ad hoc drivers:
            # y(c, (s_v, e_v)) := sum_{(c, j)} x(c, j, (s_v, e_v)) * sum_{s \in g} sum_{(s, k)} x(s, k, (s_v, e_v))
            # ----------------------------------------------------------------------------------------------------------
            for s_v, e_v in self._ad_hoc_drivers:
                self.y[(customer, (s_v, e_v))] = self._solver.BoolVar("y(%s, (%s, %s))" % (customer, s_v, e_v))
            # ----------------------------------------------------------------------------------------------------------
            # Auxiliary variables for dedicated drivers:
            # w(c, (s_v, e_v)) := sum_{(c, j)} x(c, j, (s_v, e_v)) * sum_{(s, k)} x(s, k, (s_v, e_v))
            # ----------------------------------------------------------------------------------------------------------
            for s_v, e_v in self._dedicated_drivers:
                shop = self._shop_by_F[s_v]
                if shop not in shops_customer:
                    continue
                self.w[(customer, (s_v, e_v))] = self._solver.BoolVar("w(%s, (%s, %s))" % (customer, s_v, e_v))

    def _define_ad_hoc_visits_at_most_one_shop_per_retailer_constraints(self):
        K = len(self._ad_hoc_drivers)
        constraints = [0] * len(self._shops_by_group_id) * K
        for cur_g, (_, shops) in enumerate(self._shops_by_group_id.iteritems()):
            for k, (s_v, e_v) in enumerate(self._ad_hoc_drivers):
                constraints[cur_g * K + k] = self._solver.Constraint(0.0, 1.0, str(self._solver.NumConstraints()))
                for shop in shops:
                    for j in self._working_graph[shop]:
                        coeff = constraints[cur_g * K + k].GetCoefficient(self.x[(shop, j, (s_v, e_v))])
                        constraints[cur_g * K + k].SetCoefficient(self.x[(shop, j, (s_v, e_v))], coeff + 1.0)
        check_constraints(constraints)

    # def _define_retailer_visited_at_least_once_constraints(self):
    #     constraints = [0] * len(self._shops_by_group_id)
    #     for ord_, (group_id, shops) in enumerate(self._shops_by_group_id.iteritems()):
    #         constraints[ord_] = \
    #             self._solver.Constraint(1.0, self._solver.infinity(), str(self._solver.NumConstraints()))
    #         for s_v, e_v in self._ad_hoc_drivers:
    #             for i in shops:
    #                 for j in self._working_graph[i]:
    #                     coeff = constraints[ord_].GetCoefficient(self.x[(i, j, (s_v, e_v))])
    #                     constraints[ord_].SetCoefficient(self.x[(i, j, (s_v, e_v))], coeff + 1.0)
    #         for s_v, e_v in self._dedicated_drivers:
    #             shop_start = self._shop_by_F[s_v]
    #             if shop_start not in shops:
    #                 continue
    #             for j in self._customers_by_group_id[group_id]:
    #                 coeff = constraints[ord_].GetCoefficient(self.x[(shop_start, j, (s_v, e_v))])
    #                 constraints[ord_].SetCoefficient(self.x[(shop_start, j, (s_v, e_v))], coeff + 1.0)
    #     check_constraints(constraints)

    def _define_customer_served_by_one_driver_constraints(self):
        constraints = [0] * len(self._customers_dict)
        for cur_c, (customer, group_id) in enumerate(self._customers_dict.iteritems()):
            shops_customer = self._shops_by_group_id[group_id]
            constraints[cur_c] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
            for s_v, e_v in self._ad_hoc_drivers:
                for j in self._working_graph[customer]:
                    if (j in self.H_e or j in self.F_e) and j != e_v:
                        continue
                    coeff = constraints[cur_c].GetCoefficient(self.x[(customer, j, (s_v, e_v))])
                    constraints[cur_c].SetCoefficient(self.x[(customer, j, (s_v, e_v))], coeff + 1.0)
                # for i in self.N:
                #     if i != customer:
                #         coeff = constraints[cur_c].GetCoefficient(self.x[(i, customer, (s_v, e_v))])
                #         constraints[cur_c].SetCoefficient(self.x[(i, customer, (s_v, e_v))], coeff + 1.0)
            for s_v, e_v in self._dedicated_drivers:
                shop_start = self._shop_by_F[s_v]
                if shop_start not in shops_customer:
                    continue
                coeff = constraints[cur_c].GetCoefficient(self.x[(customer, e_v, (s_v, e_v))])
                constraints[cur_c].SetCoefficient(self.x[(customer, e_v, (s_v, e_v))], coeff + 1.0)
                for j in self._customers_by_group_id[group_id]:
                    if j == customer:
                        continue
                    coeff = constraints[cur_c].GetCoefficient(self.x[(customer, j, (s_v, e_v))])
                    constraints[cur_c].SetCoefficient(self.x[(customer, j, (s_v, e_v))], coeff + 1.0)
                # coeff = constraints[cur_c].GetCoefficient(self.x[(shop_start, customer, (s_v, e_v))])
                # constraints[cur_c].SetCoefficient(self.x[(shop_start, customer, (s_v, e_v))], coeff + 1.0)
                # for i in self._customers_by_group_id[group_id]:
                #     if i != customer:
                #         coeff = constraints[cur_c].GetCoefficient(self.x[(i, customer, (s_v, e_v))])
                #         constraints[cur_c].SetCoefficient(self.x[(i, customer, (s_v, e_v))], coeff + 1.0)
        check_constraints(constraints)

    def _define_dedicated_driver_leave_at_most_once_constraints(self):
        constraints = [0] * len(self._dedicated_drivers)
        for cur_d, (s_v, e_v) in enumerate(self._dedicated_drivers):
            shop_start = self._shop_by_F[s_v]
            group_id = self._shops_dict[shop_start]
            constraints[cur_d] = self._solver.Constraint(0.0, 1.0, str(self._solver.NumConstraints()))
            for j in self._customers_by_group_id[group_id]:
                coeff = constraints[cur_d].GetCoefficient(self.x[(shop_start, j, (s_v, e_v))])
                constraints[cur_d].SetCoefficient(self.x[(shop_start, j, (s_v, e_v))], coeff + 1.0)
        check_constraints(constraints)

    def _define_same_driver_constraints(self):
        k_ = len(self._ad_hoc_drivers)
        C = len(self._customers_dict)
        constraints = \
            [0] * 3 * (C * k_ + sum([len(self._shops_by_group_id[g_id]) for g_id in self._customers_dict.values()]))
        cnt = 0
        for customer, group_id in self._customers_dict.iteritems():
            #
            shops_customer = self._shops_by_group_id[group_id]
            for s_v, e_v in self._ad_hoc_drivers:
                constraints[cnt] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
                constraints[cnt + 1] = \
                    self._solver.Constraint(0.0, self._solver.infinity(), str(self._solver.NumConstraints()))
                constraints[cnt + 2] = \
                    self._solver.Constraint(-1.0, self._solver.infinity(), str(self._solver.NumConstraints()))
                #
                coeff = constraints[cnt].GetCoefficient(self.y[customer, (s_v, e_v)])
                constraints[cnt].SetCoefficient(self.y[customer, (s_v, e_v)], coeff - 1.0)
                coeff = constraints[cnt + 1].GetCoefficient(self.y[customer, (s_v, e_v)])
                constraints[cnt + 1].SetCoefficient(self.y[customer, (s_v, e_v)], coeff - 1.0)
                coeff = constraints[cnt + 2].GetCoefficient(self.y[customer, (s_v, e_v)])
                constraints[cnt + 2].SetCoefficient(self.y[customer, (s_v, e_v)], coeff + 1.0)
                #
                for j in self._working_graph[customer]:
                    if (j in self.H_e or j in self.F_e) and j != e_v:
                        continue
                    coeff = constraints[cnt].GetCoefficient(self.x[customer, j, (s_v, e_v)])
                    constraints[cnt].SetCoefficient(self.x[customer, j, (s_v, e_v)], coeff + 1.0)
                    coeff = constraints[cnt + 2].GetCoefficient(self.x[customer, j, (s_v, e_v)])
                    constraints[cnt + 2].SetCoefficient(self.x[customer, j, (s_v, e_v)], coeff - 1.0)
                for shop in shops_customer:
                    for j in self._working_graph[shop]:
                        coeff = constraints[cnt + 1].GetCoefficient(self.x[(shop, j, (s_v, e_v))])
                        constraints[cnt + 1].SetCoefficient(self.x[(shop, j, (s_v, e_v))], coeff + 1.0)
                        coeff = constraints[cnt + 2].GetCoefficient(self.x[(shop, j, (s_v, e_v))])
                        constraints[cnt + 2].SetCoefficient(self.x[(shop, j, (s_v, e_v))], coeff - 1.0)
                #
                cnt += 3
            #
            for s_v, e_v in self._dedicated_drivers:
                shop = self._shop_by_F[s_v]
                if shop not in shops_customer:
                    continue
                constraints[cnt] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
                constraints[cnt + 1] = \
                    self._solver.Constraint(0.0, self._solver.infinity(), str(self._solver.NumConstraints()))
                constraints[cnt + 2] = \
                    self._solver.Constraint(-1.0, self._solver.infinity(), str(self._solver.NumConstraints()))
                #
                coeff = constraints[cnt].GetCoefficient(self.w[customer, (s_v, e_v)])
                constraints[cnt].SetCoefficient(self.w[customer, (s_v, e_v)], coeff - 1.0)
                coeff = constraints[cnt + 1].GetCoefficient(self.w[customer, (s_v, e_v)])
                constraints[cnt + 1].SetCoefficient(self.w[customer, (s_v, e_v)], coeff - 1.0)
                coeff = constraints[cnt + 2].GetCoefficient(self.w[customer, (s_v, e_v)])
                constraints[cnt + 2].SetCoefficient(self.w[customer, (s_v, e_v)], coeff + 1.0)
                #
                for j in self._customers_by_group_id[group_id]:
                    coeff = constraints[cnt + 1].GetCoefficient(self.x[shop, j, (s_v, e_v)])
                    constraints[cnt + 1].SetCoefficient(self.x[shop, j, (s_v, e_v)], coeff + 1.0)
                    coeff = constraints[cnt + 2].GetCoefficient(self.x[shop, j, (s_v, e_v)])
                    constraints[cnt + 2].SetCoefficient(self.x[shop, j, (s_v, e_v)], coeff - 1.0)
                    if j == customer:
                        continue
                    coeff = constraints[cnt].GetCoefficient(self.x[customer, j, (s_v, e_v)])
                    constraints[cnt].SetCoefficient(self.x[customer, j, (s_v, e_v)], coeff + 1.0)
                    coeff = constraints[cnt + 2].GetCoefficient(self.x[customer, j, (s_v, e_v)])
                    constraints[cnt + 2].SetCoefficient(self.x[customer, j, (s_v, e_v)], coeff - 1.0)
                coeff = constraints[cnt].GetCoefficient(self.x[customer, e_v, (s_v, e_v)])
                constraints[cnt].SetCoefficient(self.x[customer, e_v, (s_v, e_v)], coeff + 1.0)
                coeff = constraints[cnt + 2].GetCoefficient(self.x[customer, e_v, (s_v, e_v)])
                constraints[cnt + 2].SetCoefficient(self.x[customer, e_v, (s_v, e_v)], coeff - 1.0)
                #
                cnt += 3
        check_constraints(constraints)

    def _define_flow_conservation_locations_constraints(self):
        K = len(self._drivers)
        constraints = [0] * len(self.N) * K
        for cur_n, i in enumerate(self.N):
            for k, ((s_v, _, _), (e_v, _, _)) in enumerate(self._drivers):
                constraints[cur_n * K + k] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
                for j in self.N:
                    try:
                        coeff = constraints[cur_n * K + k].GetCoefficient(self.x[(i, j, (s_v, e_v))])
                        constraints[cur_n * K + k].SetCoefficient(self.x[(i, j, (s_v, e_v))], coeff + 1.0)
                    except KeyError:
                        pass
                    try:
                        coeff = constraints[cur_n * K + k].GetCoefficient(self.x[(j, i, (s_v, e_v))])
                        constraints[cur_n * K + k].SetCoefficient(self.x[(j, i, (s_v, e_v))], coeff - 1.0)
                    except KeyError:
                        pass
                try:
                    coeff = constraints[cur_n * K + k].GetCoefficient(self.x[(i, e_v, (s_v, e_v))])
                    constraints[cur_n * K + k].SetCoefficient(self.x[(i, e_v, (s_v, e_v))], coeff + 1.0)
                except KeyError:
                    pass
                try:
                    coeff = constraints[cur_n * K + k].GetCoefficient(self.x[(s_v, i, (s_v, e_v))])
                    constraints[cur_n * K + k].SetCoefficient(self.x[(s_v, i, (s_v, e_v))], coeff - 1.0)
                except KeyError:
                    pass
        check_constraints(constraints)

    def _define_flow_conservation_driver_constraints(self):
        K = len(self._ad_hoc_drivers)
        constraints = [0] * (2 * K + len(self._dedicated_drivers))
        for cur_d, (s_v, e_v) in enumerate(self._ad_hoc_drivers):
            constraints[cur_d] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
            for j in self._working_graph[s_v]:
                coeff = constraints[cur_d].GetCoefficient(self.x[(s_v, j, (s_v, e_v))])
                constraints[cur_d].SetCoefficient(self.x[(s_v, j, (s_v, e_v))], coeff + 1.0)
            # for j in self._shops:
            #     coeff = constraints[cur_d].GetCoefficient(self.x[(s_v, j, cur_d)])
            #     constraints[cur_d].SetCoefficient(self.x[(s_v, j, cur_d)], coeff + 1.0)
            # coeff = constraints[cur_d].GetCoefficient(self.x[(s_v, e_v, cur_d)])
            # constraints[cur_d].SetCoefficient(self.x[(s_v, e_v, cur_d)], coeff + 1.0)
            constraints[K + cur_d] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
            for i in self._customers:
                coeff = constraints[K + cur_d].GetCoefficient(self.x[(i, e_v, (s_v, e_v))])
                constraints[K + cur_d].SetCoefficient(self.x[(i, e_v, (s_v, e_v))], coeff + 1.0)
            coeff = constraints[K + cur_d].GetCoefficient(self.x[(s_v, e_v, (s_v, e_v))])
            constraints[K + cur_d].SetCoefficient(self.x[(s_v, e_v, (s_v, e_v))], coeff + 1.0)
        #
        for cur_d, (s_v, e_v) in enumerate(self._dedicated_drivers):
            shop_start = self._shop_by_F[s_v]
            group_id = self._shops_dict[shop_start]
            constraints[2 * K + cur_d] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
            for j in self._working_graph[s_v]:
                coeff = constraints[2 * K + cur_d].GetCoefficient(self.x[(s_v, j, (s_v, e_v))])
                constraints[2 * K + cur_d].SetCoefficient(self.x[(s_v, j, (s_v, e_v))], coeff + 1.0)
            for i in self._customers_by_group_id[group_id]:
                coeff = constraints[2 * K + cur_d].GetCoefficient(self.x[(i, e_v, (s_v, e_v))])
                constraints[2 * K + cur_d].SetCoefficient(self.x[(i, e_v, (s_v, e_v))], coeff - 1.0)
        check_constraints(constraints)

    def _define_time_consistency_constraints(self):
        # M = float(sys.maxint)
        # TODO: Confirm this:
        # Upper bound for start service time is the sum of the times of all arcs.
        M = sum(self._working_graph.get_edges().values())
        X = len(self.x)
        constraints = [0] * X * 4
        for cur_x, (i, j, (s_v, e_v)) in enumerate(self.x):
            #
            constraints[cur_x] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                        str(self._solver.NumConstraints()))
            coeff = constraints[cur_x].GetCoefficient(self.x[(i, j, (s_v, e_v))])
            constraints[cur_x].SetCoefficient(self.x[(i, j, (s_v, e_v))], coeff + M)
            coeff = constraints[cur_x].GetCoefficient(self.z[(i, j, (s_v, e_v))])
            constraints[cur_x].SetCoefficient(self.z[(i, j, (s_v, e_v))], coeff - 1.0)
            #
            constraints[X + cur_x] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                            str(self._solver.NumConstraints()))
            coeff = constraints[X + cur_x].GetCoefficient(self.B[(i, (s_v, e_v))])
            constraints[X + cur_x].SetCoefficient(self.B[(i, (s_v, e_v))], coeff + 1.0)
            coeff = constraints[X + cur_x].GetCoefficient(self.z[(i, j, (s_v, e_v))])
            constraints[X + cur_x].SetCoefficient(self.z[(i, j, (s_v, e_v))], coeff - 1.0)
            #
            constraints[2 * X + cur_x] = self._solver.Constraint(-M, self._solver.infinity(),
                                                                str(self._solver.NumConstraints()))
            coeff = constraints[2 * X + cur_x].GetCoefficient(self.B[(i, (s_v, e_v))])
            constraints[2 * X + cur_x].SetCoefficient(self.B[(i, (s_v, e_v))], coeff - 1.0)
            coeff = constraints[2 * X + cur_x].GetCoefficient(self.x[(i, j, (s_v, e_v))])
            constraints[2 * X + cur_x].SetCoefficient(self.x[(i, j, (s_v, e_v))], coeff - M)
            coeff = constraints[2 * X + cur_x].GetCoefficient(self.z[(i, j, (s_v, e_v))])
            constraints[2 * X + cur_x].SetCoefficient(self.z[(i, j, (s_v, e_v))], coeff + 1.0)
            #
            constraints[3 * X + cur_x] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                                str(self._solver.NumConstraints()))
            coeff = constraints[3 * X + cur_x].GetCoefficient(self.B[(j, (s_v, e_v))])
            constraints[3 * X + cur_x].SetCoefficient(self.B[(j, (s_v, e_v))], coeff + 1.0)
            coeff = constraints[3 * X + cur_x].GetCoefficient(self.x[(i, j, (s_v, e_v))])
            constraints[3 * X + cur_x].SetCoefficient(self.x[(i, j, (s_v, e_v))], coeff - self._working_graph[i][j])
            coeff = constraints[3 * X + cur_x].GetCoefficient(self.z[(i, j, (s_v, e_v))])
            constraints[3 * X + cur_x].SetCoefficient(self.z[(i, j, (s_v, e_v))], coeff - 1.0)
        check_constraints(constraints)

    def _define_precedence_constraints(self):
        K = len(self._drivers)
        k_ = len(self._ad_hoc_drivers)
        shop_numbers = [len(self._shops_by_group_id[group_id]) for group_id in self._customers_dict.values()]
        constraints = [0] * (sum(shop_numbers) * (k_ + 1) + K)
        cnt = 0
        # for req, _ in enumerate(self._requests):
        for customer, group_id in self._customers_dict.iteritems():
            shops_customer = self._shops_by_group_id[group_id]
            # for k, _ in enumerate(self._drivers):
            for s_v, e_v in self._ad_hoc_drivers:
                # for i in shops:
                for i in shops_customer:
                    constraints[cnt] = self._solver.Constraint(self._working_graph[i][customer],
                                                               self._solver.infinity(),
                                                               str(self._solver.NumConstraints()))
                    coeff = constraints[cnt].GetCoefficient(self.B[(customer, (s_v, e_v))])
                    constraints[cnt].SetCoefficient(self.B[(customer, (s_v, e_v))], coeff + 1.0)
                    coeff = constraints[cnt].GetCoefficient(self.B[(i, (s_v, e_v))])
                    constraints[cnt].SetCoefficient(self.B[(i, (s_v, e_v))], coeff - 1.0)
                    cnt += 1
            for s_v, e_v in self._dedicated_drivers:
                shop_start = self._shop_by_F[s_v]
                if shop_start not in shops_customer:
                    continue
                constraints[cnt] = self._solver.Constraint(self._working_graph[shop_start][customer],
                                                           self._solver.infinity(),
                                                           str(self._solver.NumConstraints()))
                coeff = constraints[cnt].GetCoefficient(self.B[(customer, (s_v, e_v))])
                constraints[cnt].SetCoefficient(self.B[(customer, (s_v, e_v))], coeff + 1.0)
                coeff = constraints[cnt].GetCoefficient(self.B[(shop_start, (s_v, e_v))])
                constraints[cnt].SetCoefficient(self.B[(shop_start, (s_v, e_v))], coeff - 1.0)
                cnt += 1
        for (s_v, _, _), (e_v, _, _) in self._drivers:
            constraints[cnt] = self._solver.Constraint(self._working_graph[s_v][e_v], self._solver.infinity(),
                                                       str(self._solver.NumConstraints()))
            coeff = constraints[cnt].GetCoefficient(self.B[(e_v, (s_v, e_v))])
            constraints[cnt].SetCoefficient(self.B[(e_v, (s_v, e_v))], coeff + 1.0)
            coeff = constraints[cnt].GetCoefficient(self.B[(s_v, (s_v, e_v))])
            constraints[cnt].SetCoefficient(self.B[(s_v, (s_v, e_v))], coeff - 1.0)
            cnt += 1
        check_constraints(constraints)

    def _define_threshold_constraints(self, threshold_sd=1.5):
        pairs = list()
        for s_v, e_v in self._ad_hoc_drivers:
            pairs.append((s_v, e_v))
        self._graph.compute_dist_paths(pairs=pairs, compute_paths=False)
        constraints = [0] * len(self._ad_hoc_drivers)
        for k, (s_v, e_v) in enumerate(self._ad_hoc_drivers):
            thr = self._graph.dist[tuple(sorted([s_v, e_v]))] * threshold_sd
            constraints[k] = self._solver.Constraint(0.0, thr, str(self._solver.NumConstraints()))
            for i, j, x in self.xs_by_driver[(s_v, e_v)]:
                coeff = constraints[k].GetCoefficient(x)
                constraints[k].SetCoefficient(x, coeff + self._working_graph[i][j])
        check_constraints(constraints)

    # def _define_time_window_constraints(self):
    #     constraints = [0] * len(self._working_graph)
    #     for ord_, (i, e, l) in enumerate(self._V_tws):
    #         for k, _ in enumerate(self._drivers):
    #             if (i, k) in self.B:
    #                 constraints[ord_] = self._solver.Constraint(e, l, str(self._solver.NumConstraints()))
    #                 coeff = constraints[ord_].GetCoefficient(self.B[(i, k)])
    #                 constraints[ord_].SetCoefficient(self.B[(i, k)], coeff + 1.0)

    def _define_objective(self):
        objective = self._solver.Objective()
        for (i, j, _), x in self.x.iteritems():
            coeff = objective.GetCoefficient(x)
            objective.SetCoefficient(x, coeff + self._working_graph[i][j])
        objective.SetMinimization()

    def solve(self, requests, drivers, method='MILP', verbose=False, partition_method='SP-fraction', fraction_sd=.5,
              threshold_sd=1.5, solve_partition_method='BB', solve_unserved_method='BB'):

        self._requests = requests
        self._drivers = list(drivers)

        self._pre_process_requests_drivers()

        if method == 'MILP' or method == 'MILP-threshold':
            self._solver = pywraplp.Solver("SolveIntegerProblem", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
            self._build_working_graph()
            return self._solve_milp(method, threshold_sd, verbose)

        if method == 'SP-based':
            return self._sp_based(partition_method=partition_method,
                                  fraction_sd=fraction_sd,
                                  threshold_sd=threshold_sd,
                                  solve_partition_method=solve_partition_method,
                                  solve_unserved_method=solve_unserved_method)

    def _define_milp(self, method='MILP', threshold_sd=1.5):
        self._define_vars()
        self._define_objective()
        self._define_ad_hoc_visits_at_most_one_shop_per_retailer_constraints()
        self._define_dedicated_driver_leave_at_most_once_constraints()
        self._define_customer_served_by_one_driver_constraints()
        self._define_same_driver_constraints()
        self._define_flow_conservation_locations_constraints()
        self._define_flow_conservation_driver_constraints()
        self._define_time_consistency_constraints()
        self._define_precedence_constraints()
        if method == 'MILP-threshold':
            self._define_threshold_constraints(threshold_sd)
        # self._define_time_window_constraints()

    def _solve_milp(self, method='MILP', threshold_sd=1.5, verbose=False):

        self._define_milp(method, threshold_sd)
        result_status = self._solver.Solve()
        # The problem has an optimal solution.
        # assert result_status == pywraplp.Solver.OPTIMAL
        # The solution looks legit (when using solvers other than
        # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
        assert self._solver.VerifySolution(1e-7, True)
        if result_status == pywraplp.Solver.OPTIMAL:
            # If verbose...
            if verbose:
                print('Number of variables =', self._solver.NumVariables())
                print('Number of constraints =', self._solver.NumConstraints())
                print('Optimal objective value = %d' % self._solver.Objective().Value())
                # Variables
                for _, variable in self.x.iteritems():
                    print('%s = %d' % (variable.name(), variable.solution_value()))
                for _, variable in self.B.iteritems():
                    print('%s = %d' % (variable.name(), variable.solution_value()))
                for _, variable in self.z.iteritems():
                    print('%s = %d' % (variable.name(), variable.solution_value()))
            # Return routes
            return self._build_routes_milp(), self._solver.Objective().Value()
        return None, 0

    def _pre_process_requests_drivers(self):
        customers_by_shops = dict()
        # Which customers are served by this group pf shops?
        for shops_tws, (customer, _, _) in self._requests:
            shops = tuple(sorted([shop for shop, _, _ in shops_tws]))
            try:
                customers_by_shops[shops].add(customer)
            except KeyError:
                customers_by_shops[shops] = {customer}
        # Create group ID which relates shops and customers, i.e., breaks N:N relationship.
        # Populate data structures to answer queries as follows:
        # (a) customer -> group ID -> shops
        # (b) shop -> group ID -> shops
        self._shops = set()
        self._customers = set()
        self._shops_dict = dict()
        self._customers_dict = dict()
        self._shops_by_group_id = dict()
        self._customers_by_group_id = dict()
        for shops, customers in customers_by_shops.iteritems():
            self._shops.update(shops)
            self._customers.update(customers)
            #
            group_id = id_generator()
            self._shops_dict.update({shop: group_id for shop in shops})
            self._customers_dict.update({customer: group_id for customer in customers})
            self._shops_by_group_id[group_id] = shops
            self._customers_by_group_id[group_id] = customers
        # N+ (shops), N- (customers), N := N+ U N-
        self.N = list()
        self.N.extend(self._shops)
        self.N.extend(self._customers)
        # --------------------------------------------------------------------------------------------------------------
        # Ad hoc drivers -> H+: initial locations, H-: destinations
        # --------------------------------------------------------------------------------------------------------------
        self.H_s = list()
        self.H_e = list()
        self._ad_hoc_drivers = list()
        for (start_v, _, _), (end_v, _, _) in self._drivers:
            self.H_s.append(start_v)
            self.H_e.append(end_v)
            # Update list of AD HOC drivers.
            self._ad_hoc_drivers.append((start_v, end_v))
        # --------------------------------------------------------------------------------------------------------------
        # Dedicated drivers -> F+: initial locations, F-: destinations
        # --------------------------------------------------------------------------------------------------------------
        self.F_s = list()
        self.F_e = list()
        # Maps are created to identify which shop an auxiliary vertex refers to and vice versa.
        self._shop_by_F = dict()
        self._Fs_by_shop = dict()
        self._dedicated_drivers = list()
        # Create two auxiliary vertices for each shop: initial location and destination of a dedicated driver.
        # One driver is located at each shop.
        for shop in self._shops:
            #
            start_v = self._graph.clone_node(shop)
            end_v = self._graph.clone_node(shop)
            self._graph.append_edge_2(tuple(sorted([start_v, shop])), weight=0)
            self._graph.append_edge_2(tuple(sorted([end_v, shop])), weight=0)
            #
            self.F_s.append(start_v)
            self.F_e.append(end_v)
            # Update list of DEDICATED drivers.
            self._dedicated_drivers.append((start_v, end_v))
            # Update list of drivers in general.
            self._drivers.append(((start_v, None, None), (end_v, None, None)))
            # Update maps.
            self._shop_by_F[start_v] = shop
            self._shop_by_F[end_v] = shop
            self._Fs_by_shop[shop] = (start_v, end_v)

    def _sp_based(self, partition_method='SP-fraction', fraction_sd=.5, threshold_sd=1.5, solve_partition_method='BB',
                  solve_unserved_method='BB'):
        routes = list()
        cost = 0
        partitions = \
            self._compute_partitions(method=partition_method, fraction_sd=fraction_sd, threshold_sd=threshold_sd)
        # Solve each partition
        served_customers = set()
        for partition in partitions.iteritems():
            path, c, sc = self._solve_partition(partition,
                                                method=solve_partition_method,
                                                partition_method=partition_method,
                                                threshold_sd=threshold_sd)
            routes.append(path)
            cost += c
            served_customers.update(sc)

        # Who were the non-visited customers?
        non_visited = self._customers.difference(served_customers)
        # These customers are going to be served by their nearest shop. When a dedicated vehicle starting from a
        # shop has to serve more than one customer, this becomes a new partition of the CSDP-AP problem.
        partitions = dict()
        for non_visited_customer in non_visited:
            customer_group = self._customers_dict[non_visited_customer]
            # Which shops can serve the current non-visited customer?
            shops_customer = self._shops_by_group_id[customer_group]
            dist, _ = self._graph.get_k_closest_destinations(non_visited_customer, 1, shops_customer)
            if len(dist) != 1:
                raise (RuntimeError, "SP-based: There must be at least one nearest shop to serve each customer.")
            nearest = dist.keys()[0]
            s_v, e_v = self._Fs_by_shop[nearest]
            if (s_v, e_v) not in partitions:
                partitions[(s_v, e_v)] = {'shops': {nearest}, 'customers': {non_visited_customer}}
            else:
                partitions[(s_v, e_v)]['customers'].add(non_visited_customer)
        # Solve the partitions created for the dedicated fleet.
        for partition in partitions.iteritems():
            if solve_unserved_method == 'BB':
                path, c, _ = self._solve_partition(partition)
                path = [v if v not in self._shop_by_F else self._shop_by_F[v] for v in path]
                routes.append(path)
                cost += c
            elif solve_unserved_method == 'double-tree':
                (_, _), shops_customers = partition
                vertices = shops_customers['shops'].union(shops_customers['customers'])
                complete = self._graph.build_metric_closure(vertices)
                mst = complete.compute_mst()
                shop = min(shops_customers['shops'])
                euler_tour = mst.compute_euler_tour(shop)
                contracted = list()
                for v in euler_tour:
                    if v not in contracted:
                        contracted.append(v)
                contracted.append(shop)  # Closing the loop.
                route = self._graph.expand_contracted_path(contracted)
                c = self._graph.compute_path_weight(route)
                routes.append(route)
                cost += c
            elif solve_unserved_method == 'Christofides':
                raise NotImplementedError
            else:
                raise NotImplementedError
        return routes, cost

    def _compute_partitions(self, method='SP-fraction', fraction_sd=.5, threshold_sd=1.5, tiebreaker='B-MST'):
        partitions = {}
        # Drivers' shortest paths are computed.
        # pairs = [(start_v, end_v) for start_v, end_v in self._ad_hoc_drivers]
        self._graph.compute_dist_paths(pairs=self._ad_hoc_drivers)
        #  Priority queue is built based on shortest distances.
        vehicles_pd = PriorityDictionary()
        for start_v, end_v in self._ad_hoc_drivers:
            vehicles_pd[(start_v, end_v)] = self._graph.dist[tuple(sorted([start_v, end_v]))]
        # --------------------------------------------------------------------------------------------------------------
        # SP-fraction:  Shortest-path trees are grown from drivers' shortest-path's road intersections.
        #               Drivers' shortest paths are iterated in shortest-distance ascending order as a tie-breaker for
        #               common customers between drivers.
        # --------------------------------------------------------------------------------------------------------------
        if method == 'SP-fraction':
            taken = list()
            # For each driver, a set of regions is computed. Each region corresponds to the set of shortest-path trees
            # grown from a road intersection of the original shortest path of the driver, and contains sets of shops and
            # customers.
            for start_v, end_v in vehicles_pd:
                path = self._graph.paths[tuple(sorted([start_v, end_v]))]
                dist = vehicles_pd[(start_v, end_v)]
                if tiebreaker == 'FCFA':
                    regions = self._compute_regions(path, dist, fraction_sd=fraction_sd, excluded_customers=taken)
                elif tiebreaker == 'B-MST':
                    regions = self._compute_regions(path, dist, fraction_sd=fraction_sd)
                else:
                    raise NotImplementedError
                # Shops and customers of different regions of the same driver are gathered. We are interested in
                # returning shops and customers by driver (partition) so we drop the extra level of disaggregation,
                # i.e., by region.
                shops = set()
                customers = set()
                for shops_customers in regions.values():
                    shops.update(shops_customers['shops'])
                    customers.update(shops_customers['customers'])
                partitions[(start_v, end_v)] = {'customers': customers, 'shops': shops}
                # These are the customers taken by this partition.
                if tiebreaker == 'FCFA':
                    taken.extend(customers)
        # --------------------------------------------------------------------------------------------------------------
        # SP-Voronoi:   Drivers' shortest-path-based Voronoi cells are computed.
        # --------------------------------------------------------------------------------------------------------------
        elif method == 'SP-Voronoi':
            # Drivers' paths are gathered as a list to be sent as parameter for Voronoi cells computation.
            paths = list()
            for start_v, end_v in self._ad_hoc_drivers:
                paths.append(self._graph.paths[tuple(sorted([start_v, end_v]))])
            # Voronoi cells contain all kinds of vertices, i.e., not only shops and customers. Thus, cells must be
            # sieved.
            cells, _ = self._graph.get_voronoi_paths_cells(paths)
            for (start_v, end_v), vertices in cells.iteritems():
                partitions[(start_v, end_v)] = dict()
                for vertex in vertices:
                    if vertex in self._shops:
                        try:
                            partitions[(start_v, end_v)]['shops'].add(vertex)
                        except KeyError:
                            partitions[(start_v, end_v)]['shops'] = {vertex}
                    elif vertex in self._customers:
                        try:
                            partitions[(start_v, end_v)]['customers'].add(vertex)
                        except KeyError:
                            partitions[(start_v, end_v)]['customers'] = {vertex}
        # --------------------------------------------------------------------------------------------------------------
        # SP-threshold: Vertices within ellipses with constant = SD * threshold_sd are retrieved for each driver as an
        #               initial partition. The partition must be solved accordingly, i.e., regarding the threshold, this
        #               is the initial partition only.
        # --------------------------------------------------------------------------------------------------------------
        elif method == 'SP-threshold':
            taken = list()
            for start_v, end_v in vehicles_pd:
                dist = self._graph.dist[tuple(sorted([start_v, end_v]))]
                ellipse = self._graph.nodes_within_ellipse(start_v, end_v, dist * threshold_sd)
                partitions[(start_v, end_v)] = dict()
                if tiebreaker == 'FCFA':
                    vertices_left = set(ellipse.keys()).difference(taken)
                elif tiebreaker == 'B-MST':
                    vertices_left = set(ellipse.keys())
                else:
                    raise NotImplementedError
                for vertex in vertices_left:
                    if vertex in self._shops:
                        try:
                            partitions[(start_v, end_v)]['shops'].add(vertex)
                        except KeyError:
                            partitions[(start_v, end_v)]['shops'] = {vertex}
                    elif vertex in self._customers:
                        try:
                            partitions[(start_v, end_v)]['customers'].add(vertex)
                        except KeyError:
                            partitions[(start_v, end_v)]['customers'] = {vertex}
                # These are the customers taken by this partition.
                if tiebreaker == 'FCFA':
                    if 'customers' in partitions[(start_v, end_v)]:
                        taken.extend(partitions[(start_v, end_v)]['customers'])
        else:
            raise NotImplementedError
        # In case the tiebreaker is balanced-degree MST...
        if method != 'SP-Voronoi' and tiebreaker == 'B-MST':
            # Build weighted bipartite graph and compute its MST.
            bipartite = Graph()
            drivers_by_customer = dict()
            for driver, shops_customers in partitions.iteritems():
                (start_v, end_v) = driver
                path = self._graph.paths[tuple(sorted([start_v, end_v]))]
                if 'customers' not in shops_customers:
                    continue
                for customer in shops_customers['customers']:
                    _, d, _ = self._graph.compute_dist_paths(origins=[customer], destinations=path, end_mode='first',
                                                             compute_paths=False)
                    bipartite.append_edge_2((driver, customer), weight=d[d.keys()[0]])
                    try:
                        drivers_by_customer[customer].append(driver)
                    except KeyError:
                        drivers_by_customer[customer] = [driver]
            for i in range(len(partitions) - 1):
                bipartite.append_edge_2((partitions.keys()[i], partitions.keys()[i + 1]), weight=0)
            mst = bipartite.compute_mst()
            # Balance the degree of the MST.
            quarantine = set()
            moves = 0
            while True:
                # Compute drivers' degree within the MST.
                drivers_by_degree = dict()
                degree_by_driver = dict()
                highest_degree = 0
                for v, adj in mst.iteritems():
                    if isinstance(v, tuple):  # If it is tuple, then it is a driver.
                        if v in quarantine:
                            continue
                        degree = sum([1 for w in adj if not isinstance(w, tuple)])
                        try:
                            drivers_by_degree[degree].append(v)
                        except KeyError:
                            drivers_by_degree[degree] = [v]
                        degree_by_driver[v] = degree
                        if degree > highest_degree:
                            highest_degree = degree
                if highest_degree == 1:
                    if moves == 0:
                        break
                    else:
                        quarantine.clear()
                        moves = 0
                        continue
                # Pick one of the highest-degree drivers.
                highest_degree_driver = drivers_by_degree[highest_degree][0]
                sup = sys.maxint
                while True:
                    # Pick the most expensive customer for this driver.
                    most_expensive = None
                    inf = 0
                    for customer, cost in mst[highest_degree_driver].iteritems():
                        if inf < cost < sup:
                            most_expensive = customer, cost
                            inf = cost
                    if most_expensive is None:
                        quarantine.add(highest_degree_driver)
                        break
                    # Are there more drivers who share this customer and have degree at most highest_degree - 2?
                    candidates = dict()
                    for driver in drivers_by_customer[most_expensive[0]]:
                        if driver == highest_degree_driver or driver in quarantine:
                            continue
                        if degree_by_driver[driver] <= highest_degree - 2:
                            candidates[driver] = bipartite[driver][most_expensive[0]]
                    # If there is at least one candidate driver, do the local move within the MST.
                    # Otherwise, the loop continues with the next most expensive customer.
                    if len(candidates) > 0:
                        chosen, weight = min(candidates.iteritems(), key=operator.itemgetter(1))
                        mst.drop_edge(tuple(sorted([highest_degree_driver, most_expensive[0]])))
                        mst.append_edge_2((chosen, most_expensive[0]), weight=most_expensive[1])
                        moves += 1
                        break
                    else:
                        sup = most_expensive[1]
            # Set customers in partitions according to the final balanced MST.
            for v, adj in mst.iteritems():
                if isinstance(v, tuple):  # If it is tuple, then it is a driver.
                    partitions[v]['customers'].clear()
                    partitions[v]['customers'].update({w for w in adj if not isinstance(w, tuple)})
        return partitions

    def _solve_partition(self, partition, method='BB', partition_method=None, threshold_sd=1.5):
        served_customers = set()
        # Branch-and-bound optimizes the Hamiltonian path for ONE driver. For this method, the partition must include
        # one driver only.
        if method == 'BB':
            (start_v, end_v), shops_customers = partition
            # Compute the shortest path for this driver as it is used later.
            # start_v, end_v = vehicle
            self._graph.compute_dist_paths([start_v], [end_v])
            start_end = tuple(sorted([start_v, end_v]))
            # Filter out the shops that are not in the partition.
            shops_dict = dict()
            if 'shops' in shops_customers:
                shops_dict = \
                    {k: self._shops_dict[k]
                     for k in set(self._shops_dict.keys()).intersection(shops_customers['shops'])}
            # Filter out the customers who are not in the partition and do not have a shop that can serve them.
            customers_dict = dict()
            if 'customers' in shops_customers:
                local_customers = set(self._customers_dict.keys()).intersection(shops_customers['customers'])
                for c in local_customers:
                    for s in shops_dict:
                        if self._customers_dict[c] == self._shops_dict[s]:
                            customers_dict[c] = self._customers_dict[c]
                            break
            # If there are no shops nor customers, the driver follows her original route.
            if not shops_dict or not customers_dict:
                # print start_end
                route = self._graph.paths[start_end]
                cost = self._graph.dist[start_end]
            else:
                # Otherwise, partial paths' lower bounds are stored into a priority queue.
                priority_queue = PriorityDictionary()
                # There are MORE THAN ONE initial path as there are more than one alternative pick-up locations.
                if partition_method == 'SP-threshold':
                    dist = self._graph.dist[start_end]
                    initial_paths = PartialPath.init(self._graph,
                                                     shops_dict,
                                                     customers_dict,
                                                     start_v,
                                                     end_v,
                                                     dist * threshold_sd)
                    for initial_path in initial_paths:
                        if initial_path.cust_lb > 0:
                            priority_queue[initial_path] = initial_path.cust_ub * (-1)
                else:
                    # The lower bounds must be computed taking into account only one from each group of shops each time.
                    initial_paths = PartialPath.init(self._graph,
                                                     shops_dict,
                                                     customers_dict,
                                                     start_v,
                                                     end_v)
                    for initial_path in initial_paths:
                        priority_queue[initial_path] = initial_path.dist_lb
                # If the priority dictionary is empty, it means that there weren't customers within the threshold. Thus,
                # the driver follows her original route.
                if len(priority_queue) == 0:
                    # print start_end
                    route = self._graph.paths[start_end]
                    cost = self._graph.dist[start_end]
                else:
                    partial_path = None
                    # This is the maximum number of customers to be served found out after exhausting the priority
                    # dictionary.
                    actual_cust_ub = 0
                    for p in priority_queue:
                        # Check whether ALL customers have been served. This is the termination condition.
                        if len(p.customers) == 0 and p.path[-1] == end_v:
                            if partition_method == 'SP-threshold':
                                # This is when the maximum number of customers within a threshold is found out.
                                if actual_cust_ub == 0:
                                    partial_path = p
                                    actual_cust_ub = partial_path.cust_ub
                                else:
                                    # The next time, I have to check whether the current path is cheaper and it is
                                    # serving the same maximum number of customers.
                                    if p.cust_ub == actual_cust_ub and p.dist < partial_path.dist:
                                        partial_path = p
                            else:
                                partial_path = p
                                break
                        # Expands the partial path = computes partial path's offspring.
                        offspring = p.spawn()
                        # Priority queue is fed up with the offspring.
                        if partition_method == 'SP-threshold':
                            for child in offspring:
                                # child.cust_ub >= actual_cust_ub is always true as long as the maximum number has not
                                # been found out yet.
                                if child.cust_lb > 0 and child.cust_ub >= actual_cust_ub:
                                    priority_queue[child] = child.cust_ub * (-1)
                        else:
                            for child in offspring:
                                priority_queue[child] = child.dist_lb
                    if partial_path is not None:
                        # print partial_path.path
                        served_customers = set(self._customers_dict.keys()).intersection(partial_path.path)
                        route = self._graph.expand_contracted_path(partial_path.path)
                        cost = partial_path.dist
                    else:
                        # print start_end
                        route = self._graph.paths[start_end]
                        cost = self._graph.dist[start_end]
        else:
            raise NotImplementedError
        return route, cost, served_customers

    def _compute_regions(self, path, dist, fraction_sd=.5, excluded_customers=None):
        customers = set(self._customers)
        if excluded_customers is not None:
            customers = customers.difference(excluded_customers)
        # Explore from each intermediate vertex in the path up to [dist] * [fraction_sd]
        # Find shops and customers within those explored regions.
        regions = {}  # Customers and shops by intermediate vertex.
        # shops_region_revised = dict()
        for i, vertex in enumerate(path):
            # Explore graph from each intermediate vertex in driver's shortest path until 1/2 shortest distance.
            region = self._graph.explore_upto(vertex, dist * fraction_sd)
            # Which customers are in this region?
            # customers_region = self._customers.intersection(region.keys())
            customers_region = customers.intersection(region.keys())
            # Which shops are in this region?
            shops_region = self._shops.intersection(region.keys())
            # # Which of those customers can be attended?
            # # They are going to be the ones who have at least one of their preferred shops within the same region or
            # # within a previous region.
            # customers_region_revised = set()
            # shops_region_revised[vertex] = set()
            # for customer_region in customers_region:
            #     shops_customer = self._shops_by_group_id[self._customers_dict[customer_region]]
            #     # Check within this region.
            #     temp = shops_region.intersection(shops_customer)
            #     if temp:
            #         customers_region_revised.add(customer_region)
            #         shops_region_revised[vertex].update(temp)
            #     # else:  # Otherwise, check in previous regions.
            #     # Check in previous regions, too.
            #     for j in range(i - 1, -1, -1):
            #         previous_vertex = path[j]
            #         shops_past_region = regions[previous_vertex]['shops']
            #         temp = shops_past_region.intersection(shops_customer)
            #         if temp:
            #             customers_region_revised.add(customer_region)
            #             shops_region_revised[previous_vertex].update(temp)
            #             # A break would've been efficient but it incorrectly could prevent shops in previous
            #             # regions to be included in the search space. Of course, the inclusion of the customer
            #             # into the set is not needed but luckily nothing happens as it is a set.
            # # Gather customers and shops and classify them by intermediate vertex.
            # regions[vertex] = {'customers': customers_region_revised, 'shops': shops_region}
            regions[vertex] = {'customers': customers_region, 'shops': shops_region}
        # # Update regions with shops that may serve customers, i.e., there might be shops within regions that are not
        # # used at all.
        # for vertex in path:
        #     regions[vertex]['shops'] = shops_region_revised[vertex]
        return regions

    def _build_routes_milp(self):
        routes = list()
        #
        predecessors_by_driver = dict()
        for (i, j, (s_v, e_v)), variable in self.x.iteritems():
            if variable.solution_value():
                if (s_v, e_v) not in predecessors_by_driver:
                    predecessors_by_driver[(s_v, e_v)] = {j: [i]}
                elif j not in predecessors_by_driver[(s_v, e_v)]:
                    predecessors_by_driver[(s_v, e_v)].update({j: [i]})
                else:
                    predecessors_by_driver[(s_v, e_v)][j].append(i)
        contracted = list()
        for (s_v, e_v), predecessors in predecessors_by_driver.iteritems():
            route = [e_v]
            while route[-1] != s_v:
                ps = predecessors[route[-1]]
                i = 0
                if len(ps) > 1:
                    while route[-1] not in predecessors[ps[i]]:
                        i += 1
                route.append(ps[i])
                del ps[i]
            route = [v if v not in self._shop_by_F else self._shop_by_F[v] for v in route]
            route.reverse()
            contracted.append(route)
        for route in contracted:
            # print route
            routes.append(self._graph.expand_contracted_path(route))
        return routes

    def print_milp_constraints(self):
        vars_ = list()
        vars_.extend(self.x.values())
        vars_.extend(self.B.values())
        vars_.extend(self.z.values())
        for nc in range(self._solver.NumConstraints()):
            c = self._solver.LookupConstraint(str(nc))
            cs = ""
            if c.lb() != c.ub() and c.lb() > -self._solver.infinity():
                cs = str(c.lb()) + " <= "
            coeff_diff_zero = False
            for variable in vars_:
                try:
                    coeff = c.GetCoefficient(variable)
                    if coeff > 0:
                        cs += "+ " + str(coeff) + " " + variable.name() + " "
                        coeff_diff_zero = True
                    elif coeff < 0:
                        cs += "- " + str(abs(coeff)) + " " + variable.name() + " "
                        coeff_diff_zero = True
                except KeyError:
                    pass
            if not coeff_diff_zero:
                print "WARNING: Constraint %d is not needed!" % nc
            if c.lb() != c.ub() and c.ub() < self._solver.infinity():
                cs += "<= " + str(c.ub())
            elif c.lb() == c.ub():
                cs += "= " + str(c.ub())
            print cs


class PartialPath:
    """
    Partial path when computing an optimal Hamiltonian path by using branch-and-bound.
    """

    # Graph distances may be updated by an instance which in turn may benefit others.
    _graph = Graph()
    _shops_dict = dict()  # Shop with corresponding group ID.
    _custs_dict = dict()
    _shops_by_group_id = dict()  # Group ID with corresponding shops.
    _customers_by_group_id = dict()  # Group ID with corresponding customers.
    _shops_set = set()
    _customers_set = set()
    _groups_set = set()
    _origin = None
    _destination = None
    _threshold = None

    @staticmethod
    def init(graph, shops_dict, customers_dict, origin, destination, threshold=None):
        """
        Parameters
        ----------
        :param graph: Digraph
            Used to retrieve shortest distances. It may be updated by an instance which in turn benefits others.
        :param shops_dict: dict
            Shop as key and group ID as value.
        :param customers_dict: dict
            Customer as key and group ID as value.
        :param origin: graph vertex
            Where the Hamiltonian path starts from.
        :param destination: graph vertex
            Where the Hamiltonian path finishes.
        :param threshold: float
            Upper bound for the Hamiltonian path's distance.
        :return:
        """
        PartialPath._graph = graph
        # PartialPath._shops_dict = shops_dict
        PartialPath._origin = origin
        PartialPath._destination = destination
        PartialPath._threshold = threshold

        PartialPath._groups_set = set(shops_dict.values()).intersection(customers_dict.values())
        PartialPath._shops_dict = \
            {shop: g_id for shop, g_id in shops_dict.iteritems() if g_id in PartialPath._groups_set}
        PartialPath._custs_dict = \
            {cust: g_id for cust, g_id in customers_dict.iteritems() if g_id in PartialPath._groups_set}

        PartialPath._shops_set = set(PartialPath._shops_dict.keys())
        PartialPath._customers_set = set(PartialPath._custs_dict.keys())

        # Populate auxiliary shops and customers dictionaries indexed by group ID.
        PartialPath._shops_by_group_id = dict()
        # for shop, group_id in shops_dict.iteritems():
        for shop, group_id in PartialPath._shops_dict.iteritems():
            try:
                PartialPath._shops_by_group_id[group_id].add(shop)
            except KeyError:
                PartialPath._shops_by_group_id[group_id] = {shop}
        #
        PartialPath._customers_by_group_id = dict()
        for customer, group_id in customers_dict.iteritems():
            if group_id not in PartialPath._groups_set:
                continue
            try:
                PartialPath._customers_by_group_id[group_id].add(customer)
            except KeyError:
                PartialPath._customers_by_group_id[group_id] = {customer}

        # Create the initial paths. There is more than one tree in the branch and bound optimization process since the
        # pickup points are mutually exclusive within each group. Therefore, there are as many trees as the sum over all
        # shops where, for each shop, the number of trees is the number of combinations of shops from different groups.
        initial_paths = []
        # The initial paths all start from the origin and go to a shop.
        for shop, group_id in PartialPath._shops_dict.iteritems():
            # For each shop, the shops from the other groups are retrieved as we need the combinations of them.
            other_group_ids = PartialPath._groups_set.difference([group_id])
            other_groups = [PartialPath._shops_by_group_id[gi] for gi in other_group_ids]
            # Compute the combinations of shops where each combination has a shop from each group.
            combs_shops = set(product(*other_groups))
            # Create the initial paths as such. Each path starts with the origin. The next vertex in the path is the
            # current shop.
            for comb_shops in combs_shops:
                path = PartialPath([PartialPath._origin], 0, comb_shops, PartialPath._custs_dict.keys())
                path._append_vertex(shop)
                initial_paths.append(path)
        return initial_paths

    def __init__(self, path, dist, shops, customers):
        """
        Parameters
        ----------
        :param path: list
            It is specially useful when a partial path spawns offspring.
        :param dist: float
            Traveled distance.
        :param shops: Iterable
            Shops that can be part of the path and are not in it yet.
        :param customers: Iterable
            Customers that can be part of the path and are not in it yet.
        """
        self.path = list(path)
        self.dist_lb = 0
        self.cust_ub = 0
        self.cust_lb = 0
        self.dist = dist
        self.shops = set(shops)  # Contains non-visited shops only.
        self.customers = set(customers)  # Contains non-visited customers only. It is exhausted as they are visited.

    def spawn(self):
        """
        Create offspring where each child is one of the possible candidate vertices to visit. It is important that
        each child inherits the list of shops 'self.shops' and customers 'self.customers' to be visited.

        :return: list
            Offspring.
        """
        offspring = []
        to_ = self._where_to(self.path[-1])
        for vertex in to_:
            child = PartialPath(self.path, self.dist, self.shops, self.customers)
            child._append_vertex(vertex)
            offspring.append(child)
        return offspring

    def _append_vertex(self, vertex):
        """
        Appends a vertex at the end of the path. In turn, updates the traveled distance and the lower bound.

        Parameters
        ----------
        :param vertex: graph vertex
            Vertex to be appended.
        :return:
        """
        if not self.path:
            self.path = [vertex]
            self.dist = 0  # No distance when there is one vertex in the path.
        else:
            path_end = self.path[-1]
            PartialPath._graph.compute_dist_paths([path_end], [vertex], compute_paths=False)
            self.path.append(vertex)
            self.dist = self.dist + PartialPath._graph.dist[tuple(sorted([path_end, vertex]))]
        # Update non-visited shops and customers.
        if PartialPath._threshold:
            # Shops and customers that may be visited within a threshold are computed.
            ellipse = \
                self._graph.nodes_within_ellipse(vertex, PartialPath._destination, PartialPath._threshold - self.dist)
            non_visited = set(ellipse.keys()).difference(self.path)
            self.shops = self.shops.intersection(non_visited)
            customers = self.customers.intersection(non_visited)
            # Customers who cannot be served by any shop are filtered out.
            self.customers = set()
            visited_shops = PartialPath._shops_set.intersection(self.path)
            all_shops = set(visited_shops)
            all_shops.update(self.shops)
            groups = {PartialPath._shops_dict[shop] for shop in all_shops}
            for group in groups:
                if group not in PartialPath._customers_by_group_id:
                    continue
                self.customers.update(PartialPath._customers_by_group_id[group].intersection(customers))
            # Update the upper and lower bounds for visited customers.
            self._compute_cust_bs()
        else:
            self.shops.discard(vertex)
            self.customers.discard(vertex)
            # Update the distance lower bound.
            self._compute_dist_lb()

    def _compute_dist_lb(self):
        """
        Compute the lower bound. This may be thought as a matrix where the row entries are the starting points and the
        column entries are the destinations.

        :return:
        """
        mins_row_wise = dict()  # Minimum value by row (starting point).
        dist_col_wise = dict()  # Distances by destination and starting point.
        # The 'matrix' rows are computed mainly based on the vertices already in the path.
        for vertex in self._lb_from_where():
            # For each row, the candidate columns are computed.
            candidates_to = self._lb_where_to(vertex)
            PartialPath._graph.compute_dist_paths([vertex], candidates_to, compute_paths=False)
            # A list of distances by row is needed to compute the minimum by row after.
            # Here we also fill the distances-by-destination-and-starting-point data structure.
            dist_row_wise = list()
            for to_ in candidates_to:
                dist = PartialPath._graph.dist[tuple(sorted([vertex, to_]))]
                dist_row_wise.append(dist)
                try:
                    dist_col_wise[to_][vertex] = dist
                except KeyError:
                    dist_col_wise[to_] = {vertex: dist}
            mins_row_wise[vertex] = 0
            if dist_row_wise:
                mins_row_wise[vertex] = min(dist_row_wise)
        # The distances by destination are updated with the value after subtracting the minimum by row.
        # Then, the minimums by column are also saved.
        mins_col_wise = list()
        for to_, vertices in dist_col_wise.iteritems():
            for vertex in vertices:
                dist_col_wise[to_][vertex] -= mins_row_wise[vertex]
            if dist_col_wise[to_].values():
                mins_col_wise.append(min(dist_col_wise[to_].values()))
        # The lower bound is the sum of the row- and column-wise minimum values and path distance so far.
        self.dist_lb = sum(mins_row_wise.values()) + sum(mins_col_wise) + self.dist

    def _compute_cust_bs(self):
        # The minimum number of customers (lower bound) to visit is the current number of already visited customers and
        # at least one more from the set of non-visited customers. IMPORTANT: Customers who cannot be served by any shop
        # were filtered out.
        visited_customers = PartialPath._customers_set.intersection(self.path)
        self.cust_lb = len(visited_customers) + (1 if len(self.customers) > 0 else 0)
        # The maximum number of customers (upper bound) to visit is the current number of already visited customers and
        # the number of non-visited customers.
        self.cust_ub = len(visited_customers) + len(self.customers)

    def _where_to(self, from_):
        """
        What are the possible next vertices to visit from a specific vertex?

        :param from_: graph vertex
            Current vertex for which the possible vertices to visit after are computed.
        :return: set
            Vertices to visit.
        """
        to_ = set()
        visited_shops = PartialPath._shops_set.intersection(self.path)
        visited_groups = {PartialPath._shops_dict[visited_shop] for visited_shop in visited_shops}
        non_visited_groups = PartialPath._groups_set.difference(visited_groups)
        # Shops in non-visited groups.
        for non_visited_group in non_visited_groups:
            if non_visited_group not in PartialPath._shops_by_group_id:
                continue
            to_.update(PartialPath._shops_by_group_id[non_visited_group].intersection(self.shops))
        # Non-visited customers in visited groups.
        for visited_group in visited_groups:
            if visited_group not in PartialPath._customers_by_group_id:
                continue
            to_.update(PartialPath._customers_by_group_id[visited_group].intersection(self.customers))
        # Is it from a customer?
        if from_ in PartialPath._customers_set:
            # Then, it is possible to go to the destination.
            to_.add(PartialPath._destination)
        return to_

    def _lb_where_to(self, from_):
        """
        What are the possible vertices to visit from a specific vertex when computing the lower bound?
        This is different from the '_where_to' method as in this case we can visit any customer as long as it has not
        been visited yet. Also, the shops to be visited are the ones sent as parameter when an instance is created.

        :param from_: graph vertex
            Current vertex for which the possible vertices to visit are computed.
        :return: set
            Vertices to visit.
        """
        # Non-visited shops.
        to_ = set(self.shops)
        # Non-visited customers.
        to_.update(self.customers)
        # Prevent visiting itself.
        to_.discard(from_)
        # Destination is possible when it is a customer.
        if from_ in PartialPath._customers_set:
            to_.add(PartialPath._destination)
        return to_

    def _lb_from_where(self):
        """
        What are the possible vertices where to start from when computing the lower bound?

        :return: set
            Vertices to start from.
        """
        # The last vertex in the path.
        from_ = {self.path[-1]}
        # Non-visited shops.
        from_.update(self.shops)
        # Non-visited customers.
        from_.update(self.customers)
        return from_

    # def transform_to_actual_path(self):
    #     pairs = list()
    #     for i in range(len(self.path) - 1):
    #         v = self.path[i]
    #         w = self.path[i + 1]
    #         pairs.append((v, w))
    #     PartialPath._graph.compute_dist_paths(pairs=pairs, recompute=True)
    #     actual_path = [PartialPath._origin]
    #     for i in range(len(self.path) - 1):
    #         v = self.path[i]
    #         w = self.path[i + 1]
    #         path = PartialPath._graph.paths[tuple(sorted([v, w]))]
    #         if w == path[0]:
    #             path.reverse()
    #         actual_path.extend(path[1:])
    #     return actual_path
