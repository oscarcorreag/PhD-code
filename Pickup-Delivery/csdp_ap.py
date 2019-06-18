from digraph import Digraph
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


class CsdpAp:
    def __init__(self, graph):
        # self._graph = Digraph(undirected=False)
        self._graph = Digraph()
        self._graph.append_from_graph(graph)
        self._working_graph = Digraph(undirected=False)

        self._vehicles = list()
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
        self._shops_by_req = dict()
        self._customers_by_req = dict()

        self._shops_dict = dict()
        self._customers_dict = dict()
        self._shops_by_group_id = dict()
        # self._customers_by_group_id = dict()

        # self.N_cl_pl = dict()

        self.N = list()
        self.M_s = list()
        self.M_e = list()
        self.M = list()
        self._V_tws = dict()  # All vertices each with its time window.
        # --------------------------------------------------------------------------------------------------------------
        # MILP
        # --------------------------------------------------------------------------------------------------------------
        self._solver = pywraplp.Solver("SolveIntegerProblem", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        self.x = dict()
        self.B = dict()
        self.z = dict()

    def _define_vertex_subsets(self):
        # N+, N-, N := N+ U N-, N(r)+, N(r)-
        # Retrieve time windows of shops and customers.
        for req, (shops_tws, (customer, e_c, l_c)) in enumerate(self._requests):
            shops = list()
            for shop, e_s, l_s in shops_tws:
                shops.append(shop)
                self._V_tws[shop] = (e_s, l_s)
            self._shops_by_req[req] = shops
            self._customers_by_req[req] = customer
            # self.N_cl_pl[customer] = shops  # Shops by customer
            self._shops.update(shops)
            self._customers.add(customer)
            self._V_tws[customer] = (e_c, l_c)
        self.N.extend(self._shops)
        self.N.extend(self._customers)
        # M+, M-, M := M+ U M-
        # Retrieve time windows of vehicles.
        for (start_v, e_sv, l_sv), (end_v, e_ev, l_ev) in self._vehicles:
            self.M_s.append(start_v)
            self.M_e.append(end_v)
            self._V_tws[start_v] = (e_sv, l_sv)
            self._V_tws[end_v] = (e_ev, l_ev)
        self.M.extend(self.M_s)
        self.M.extend(self.M_e)

    def _define_arc_subsets(self):
        # Arc subset A1: From each vehicle start location to each pick-up location.
        for i in self.M_s:
            for j in self._shops:
                self.A1.append((i, j))
        # Arc subset A2: Between pick-up locations from different requests.
        for req_i, shops_i in self._shops_by_req.iteritems():
            for req_j, shops_j in self._shops_by_req.iteritems():
                if req_i != req_j:
                    for i in shops_i:
                        for j in shops_j:
                            self.A2.append((i, j))
        # Arc subset A3: From each pick-up location to each on-line customer location.
        for i in self._shops:
            for j in self._customers:
                self.A3.append((i, j))
        # Arc subset A4: From each on-line customer location to pick-up locations of a different request.
        for req_i, i in self._customers_by_req.iteritems():
            for req_j, shops_j in self._shops_by_req.iteritems():
                if req_i != req_j:
                    for j in shops_j:
                        self.A4.append((i, j))
        # Arc subset A5: Between on-line customer locations.
        for i in self._customers:
            for j in self._customers:
                if i != j:
                    self.A5.append((i, j))
        # Arc subset A6: From each on-line customer location to each vehicle end location.
        for i in self._customers:
            for j in self.M_e:
                self.A6.append((i, j))
        # Arc subset A7: From a vehicle start location to the same-vehicle end location.
        for (i, _, _), (j, _, _) in self._vehicles:
            self.A7.append((i, j))

    def _build_working_graph(self):
        # Shortest distances in the original graph are the weights of the arcs in the working graph.
        self._graph.compute_dist_paths(compute_paths=False)
        # Build vertex and arc sets.
        self._define_vertex_subsets()
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
        for i, j in A:
            self._working_graph.append_edge_2((i, j), weight=self._graph.dist[(i, j)])

    def _define_vars(self):
        # --------------------------------------------------------------------------------------------------------------
        # Boolean variables associated with combinations of arcs and vehicles.
        # --------------------------------------------------------------------------------------------------------------
        # These variables are defined over a subset of A1. Defining a x(i, j, k) for which i != k^+ does not make sense.
        for i, j in self.A1:
            for k, ((start_v, _, _), _) in enumerate(self._vehicles):
                if i == start_v:
                    self.x[(i, j, k)] = self._solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # These variables are defined over A2 U A3 U A4 U A5.
        A_ = list()
        A_.extend(self.A2)
        A_.extend(self.A3)
        A_.extend(self.A4)
        A_.extend(self.A5)
        for i, j in A_:
            for k, _ in enumerate(self._vehicles):
                self.x[(i, j, k)] = self._solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # These variables are defined over a subset of A6. Defining a x(i, j, k) for which j != k^- does not make sense.
        for i, j in self.A6:
            for k, (_, (end_v, _, _)) in enumerate(self._vehicles):
                if j == end_v:
                    self.x[(i, j, k)] = self._solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # These variables are defined over a subset of A7. Defining a x(i, j, k) for which i != k^+ or j != k^- does not
        # make sense. However, validating i and j is not needed as arcs {(i, j) : i = k^+ and j != k^-} are not created.
        for i, j in self.A7:
            for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
                if i == start_v and j == end_v:
                    self.x[(i, j, k)] = self._solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # --------------------------------------------------------------------------------------------------------------
        # Time variables at which vehicles start servicing at vertices.
        # Time window constraints are defined implicitly.
        # --------------------------------------------------------------------------------------------------------------
        for i in self.N:
            for k, _ in enumerate(self._vehicles):
                # self.B[(i, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (i, k))
                self.B[(i, k)] = self._solver.NumVar(self._V_tws[i][0], self._V_tws[i][1], 'B(%d, %d)' % (i, k))
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            # self.B[(start_v, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (start_v, k))
            self.B[(start_v, k)] = self._solver.NumVar(self._V_tws[start_v][0], self._V_tws[start_v][1],
                                                       'B(%d, %d)' % (start_v, k))
            # self.B[(end_v, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (end_v, k))
            self.B[(end_v, k)] = self._solver.NumVar(self._V_tws[end_v][0], self._V_tws[end_v][1],
                                                     'B(%d, %d)' % (end_v, k))
        # --------------------------------------------------------------------------------------------------------------
        # Auxiliary variables z := x(i, j, k) * B(i, k).
        # --------------------------------------------------------------------------------------------------------------
        for i, j, k in self.x:
            self.z[(i, j, k)] = self._solver.NumVar(0.0, self._solver.infinity(), 'z(%d, %d, %d)' % (i, j, k))

    def _define_one_vehicle_one_pickup_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * len(self._requests) * K
        for req, _ in enumerate(self._requests):
            shops = self._shops_by_req[req]
            for k, _ in enumerate(self._vehicles):
                constraints[req * K + k] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
                for i in shops:
                    for j, _ in self._working_graph[i].iteritems():
                        coeff = constraints[req * K + k].GetCoefficient(self.x[(i, j, k)])
                        constraints[req * K + k].SetCoefficient(self.x[(i, j, k)], coeff + 1.0)

    def _define_same_vehicle_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * len(self._requests) * K
        for req, _ in enumerate(self._requests):
            shops = self._shops_by_req[req]
            customer = self._customers_by_req[req]
            for k, _ in enumerate(self._vehicles):
                constraints[req * K + k] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
                for i in shops:
                    for j, _ in self._working_graph[i].iteritems():
                        coeff = constraints[req * K + k].GetCoefficient(self.x[(i, j, k)])
                        constraints[req * K + k].SetCoefficient(self.x[(i, j, k)], coeff + 1.0)
                for j in self.N:  # [N = (only possible) origins] TO customers.
                    if j != customer:
                        coeff = constraints[req * K + k].GetCoefficient(self.x[(j, customer, k)])
                        constraints[req * K + k].SetCoefficient(self.x[(j, customer, k)], coeff - 1.0)

    def _define_flow_conservation_locations_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * len(self.N) * K
        for ord_, i in enumerate(self.N):
            for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
                constraints[ord_ * K + k] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
                for j in self.N:
                    try:
                        coeff = constraints[ord_ * K + k].GetCoefficient(self.x[(j, i, k)])
                        constraints[ord_ * K + k].SetCoefficient(self.x[(j, i, k)], coeff + 1.0)
                    except KeyError:
                        pass
                    try:
                        coeff = constraints[ord_ * K + k].GetCoefficient(self.x[(i, j, k)])
                        constraints[ord_ * K + k].SetCoefficient(self.x[(i, j, k)], coeff - 1.0)
                    except KeyError:
                        pass
                try:
                    coeff = constraints[ord_ * K + k].GetCoefficient(self.x[(start_v, i, k)])
                    constraints[ord_ * K + k].SetCoefficient(self.x[(start_v, i, k)], coeff + 1.0)
                except KeyError:
                    pass
                try:
                    coeff = constraints[ord_ * K + k].GetCoefficient(self.x[(i, end_v, k)])
                    constraints[ord_ * K + k].SetCoefficient(self.x[(i, end_v, k)], coeff - 1.0)
                except KeyError:
                    pass

    def _define_flow_conservation_vehicle_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * 2 * K
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            constraints[k] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
            for j in self._shops:
                coeff = constraints[k].GetCoefficient(self.x[(start_v, j, k)])
                constraints[k].SetCoefficient(self.x[(start_v, j, k)], coeff + 1.0)
            coeff = constraints[k].GetCoefficient(self.x[(start_v, end_v, k)])
            constraints[k].SetCoefficient(self.x[(start_v, end_v, k)], coeff + 1.0)
            constraints[K + k] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
            for j in self._customers:
                coeff = constraints[K + k].GetCoefficient(self.x[(j, end_v, k)])
                constraints[K + k].SetCoefficient(self.x[(j, end_v, k)], coeff + 1.0)
            coeff = constraints[K + k].GetCoefficient(self.x[(start_v, end_v, k)])
            constraints[K + k].SetCoefficient(self.x[(start_v, end_v, k)], coeff + 1.0)

    def _define_time_consistency_constraints(self):
        # M = float(sys.maxint)
        # TODO: Confirm this:
        # Upper bound for start service time is the sum of the times of all arcs.
        M = sum(self._working_graph.get_edges().values())
        X = len(self.x)
        constraints = [0] * X * 4
        for ord_, (i, j, k) in enumerate(self.x):
            #
            constraints[ord_] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                        str(self._solver.NumConstraints()))
            coeff = constraints[ord_].GetCoefficient(self.x[(i, j, k)])
            constraints[ord_].SetCoefficient(self.x[(i, j, k)], coeff + M)
            coeff = constraints[ord_].GetCoefficient(self.z[(i, j, k)])
            constraints[ord_].SetCoefficient(self.z[(i, j, k)], coeff - 1.0)
            #
            constraints[X + ord_] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                            str(self._solver.NumConstraints()))
            coeff = constraints[X + ord_].GetCoefficient(self.B[(i, k)])
            constraints[X + ord_].SetCoefficient(self.B[(i, k)], coeff + 1.0)
            coeff = constraints[X + ord_].GetCoefficient(self.z[(i, j, k)])
            constraints[X + ord_].SetCoefficient(self.z[(i, j, k)], coeff - 1.0)
            #
            constraints[2 * X + ord_] = self._solver.Constraint(-M, self._solver.infinity(),
                                                                str(self._solver.NumConstraints()))
            coeff = constraints[2 * X + ord_].GetCoefficient(self.B[(i, k)])
            constraints[2 * X + ord_].SetCoefficient(self.B[(i, k)], coeff - 1.0)
            coeff = constraints[2 * X + ord_].GetCoefficient(self.x[(i, j, k)])
            constraints[2 * X + ord_].SetCoefficient(self.x[(i, j, k)], coeff - M)
            coeff = constraints[2 * X + ord_].GetCoefficient(self.z[(i, j, k)])
            constraints[2 * X + ord_].SetCoefficient(self.z[(i, j, k)], coeff + 1.0)
            #
            constraints[3 * X + ord_] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                                str(self._solver.NumConstraints()))
            coeff = constraints[3 * X + ord_].GetCoefficient(self.B[(j, k)])
            constraints[3 * X + ord_].SetCoefficient(self.B[(j, k)], coeff + 1.0)
            coeff = constraints[3 * X + ord_].GetCoefficient(self.x[(i, j, k)])
            constraints[3 * X + ord_].SetCoefficient(self.x[(i, j, k)], coeff - self._working_graph[i][j])
            coeff = constraints[3 * X + ord_].GetCoefficient(self.z[(i, j, k)])
            constraints[3 * X + ord_].SetCoefficient(self.z[(i, j, k)], coeff - 1.0)

    def _define_precedence_constraints(self):
        K = len(self._vehicles)
        # constraints = [0] * ((len(self._shops) + 1) * K)
        constraints = [0] * ((sum([len(self._shops_by_req[req]) for req in range(len(self._requests))]) + 1) * K)
        cnt = 0
        for req, _ in enumerate(self._requests):
            shops = self._shops_by_req[req]
            customer = self._customers_by_req[req]
            for k, _ in enumerate(self._vehicles):
                for i in shops:
                    constraints[cnt] = self._solver.Constraint(self._working_graph[i][customer],
                                                               self._solver.infinity(),
                                                               str(self._solver.NumConstraints()))
                    coeff = constraints[cnt].GetCoefficient(self.B[(customer, k)])
                    constraints[cnt].SetCoefficient(self.B[(customer, k)], coeff + 1.0)
                    coeff = constraints[cnt].GetCoefficient(self.B[(i, k)])
                    constraints[cnt].SetCoefficient(self.B[(i, k)], coeff - 1.0)
                    cnt += 1
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            constraints[cnt] = self._solver.Constraint(self._working_graph[start_v][end_v], self._solver.infinity(),
                                                       str(self._solver.NumConstraints()))
            coeff = constraints[cnt].GetCoefficient(self.B[(end_v, k)])
            constraints[cnt].SetCoefficient(self.B[(end_v, k)], coeff + 1.0)
            coeff = constraints[cnt].GetCoefficient(self.B[(start_v, k)])
            constraints[cnt].SetCoefficient(self.B[(start_v, k)], coeff - 1.0)
            cnt += 1

    def _define_time_window_constraints(self):
        constraints = [0] * len(self._working_graph)
        for ord_, (i, e, l) in enumerate(self._V_tws):
            for k, _ in enumerate(self._vehicles):
                if (i, k) in self.B:
                    constraints[ord_] = self._solver.Constraint(e, l, str(self._solver.NumConstraints()))
                    coeff = constraints[ord_].GetCoefficient(self.B[(i, k)])
                    constraints[ord_].SetCoefficient(self.B[(i, k)], coeff + 1.0)

    def _define_objective(self):
        objective = self._solver.Objective()
        for (i, j, _), x in self.x.iteritems():
            coeff = objective.GetCoefficient(x)
            objective.SetCoefficient(x, coeff + self._working_graph[i][j])
        objective.SetMinimization()

    def solve(self, requests, vehicles, method='MILP', verbose=False, partition_method='SP-fraction', fraction_sd=.5,
              threshold_sd=1.5, solve_partition_method='BB'):

        self._requests = requests
        self._vehicles = vehicles

        if method == 'MILP':
            self._build_working_graph()
            return self._solve_milp(verbose)

        if method == 'SP-based':
            self._pre_process_requests()
            return self._sp_based(partition_method=partition_method, fraction_sd=fraction_sd, threshold_sd=threshold_sd,
                                  solve_partition_method=solve_partition_method)

    def _define_milp(self):
        self._define_vars()
        self._define_objective()
        self._define_one_vehicle_one_pickup_constraints()
        self._define_same_vehicle_constraints()
        self._define_flow_conservation_locations_constraints()
        self._define_flow_conservation_vehicle_constraints()
        self._define_time_consistency_constraints()
        self._define_precedence_constraints()
        # self._define_time_window_constraints()

    def _solve_milp(self, verbose=False):

        self._define_milp()
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

    def _pre_process_requests(self):
        customers_by_shops = dict()
        #
        for shops_tws, (customer, _, _) in self._requests:
            shops = tuple(sorted([shop for shop, _, _ in shops_tws]))
            try:
                customers_by_shops[shops].add(customer)
            except KeyError:
                customers_by_shops[shops] = {customer}
        #
        for shops, customers in customers_by_shops.iteritems():
            group_id = id_generator()
            self._shops_by_group_id[group_id] = shops
            self._shops_dict.update({shop: group_id for shop in shops})
            self._customers_dict.update({customer: group_id for customer in customers})
            self._shops.update(shops)
            self._customers.update(customers)

    def _sp_based(self, partition_method='SP-fraction', fraction_sd=.5, threshold_sd=1.5, solve_partition_method='BB'):
        routes = list()
        cost = 0
        partitions = \
            self._compute_partitions(method=partition_method, fraction_sd=fraction_sd, threshold_sd=threshold_sd)
        # Solve each partition
        for partition in partitions.iteritems():
            path, c = self._solve_partition(partition,
                                            method=solve_partition_method,
                                            partition_method=partition_method,
                                            threshold_sd=threshold_sd)
            routes.append(path)
            cost += c

        # Who were the non-visited customers?
        visited = {v for route in routes for v in route}
        non_visited = self._customers.difference(visited)
        # These customers are going to be served by their nearest shop. The cost for each non-visited customer is twice
        # the shortest distance between such customer and her nearest shop.
        for non_visited_customer in non_visited:
            customer_group = self._customers_dict[non_visited_customer]
            # Which shops can serve the current non-visited customer?
            shops_customer = self._shops_by_group_id[customer_group]
            dist, paths = self._graph.get_k_closest_destinations(non_visited_customer, 1, shops_customer)
            if len(dist) != 1:
                raise (RuntimeError, "SP-based: There must be at least one nearest shop able to serve each customer.")
            for nearest, d in dist.iteritems():
                # IMPORTANT: We are assuming shortest path is the SAME in both directions.
                cost += (2 * d)
                from_customer_path = paths[nearest]
                path = from_customer_path[::-1][:-1]
                path.extend(from_customer_path)
                routes.append(path)
        return routes, cost

    def _compute_partitions(self, method='SP-fraction', fraction_sd=.5, threshold_sd=1.5):
        partitions = {}
        # Drivers' shortest paths are computed.
        pairs = [(start_v, end_v) for (start_v, _, _), (end_v, _, _) in self._vehicles]
        self._graph.compute_dist_paths(pairs=pairs)
        #  Priority queue is built based on shortest distances.
        vehicles_pd = PriorityDictionary()
        for vehicle in self._vehicles:
            (start_v, _, _), (end_v, _, _) = vehicle
            vehicles_pd[vehicle] = self._graph.dist[tuple(sorted([start_v, end_v]))]
        # --------------------------------------------------------------------------------------------------------------
        # SP-fraction:  Shortest-path trees are grown from drivers' shortest-path's road intersections.
        #               Drivers' shortest paths are iterated in shortest-distance ascending order as a tie-breaker for
        #               common customers between drivers.
        # --------------------------------------------------------------------------------------------------------------
        if method == 'SP-fraction':
            taken = list()
            # For each driver, a set of regions is computed. Each region corresponds to a road intersection of the
            # shortest path of the driver and contains sets of shops and customers.
            for vehicle in vehicles_pd:
                (start_v, _, _), (end_v, _, _) = vehicle
                path = self._graph.paths[tuple(sorted([start_v, end_v]))]
                dist = vehicles_pd[vehicle]
                regions = self._compute_regions(path, dist, fraction_sd=fraction_sd, excluded_customers=taken)
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
                taken.extend(customers)
        # --------------------------------------------------------------------------------------------------------------
        # SP-Voronoi:   Drivers' shortest-path-based Voronoi cells are computed.
        # --------------------------------------------------------------------------------------------------------------
        elif method == 'SP-Voronoi':
            # Drivers' paths are gathered as a list to be sent as parameter for Voronoi cells computation.
            paths = list()
            for vehicle in self._vehicles:
                (start_v, _, _), (end_v, _, _) = vehicle
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
            for vehicle in vehicles_pd:
                (start_v, _, _), (end_v, _, _) = vehicle
                dist = self._graph.dist[tuple(sorted([start_v, end_v]))]
                ellipse = self._graph.nodes_within_ellipse(start_v, end_v, dist * threshold_sd)
                partitions[(start_v, end_v)] = dict()
                vertices_left = set(ellipse.keys()).difference(taken)
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
                if 'customers' in partitions[(start_v, end_v)]:
                    taken.extend(partitions[(start_v, end_v)]['customers'])
        else:
            raise NotImplementedError
        return partitions

    def _solve_partition(self, partition, method='BB', partition_method='SP-fraction', threshold_sd=1.5):
        route = list()
        cost = 0
        # Branch-and-bound optimizes the Hamiltonian path for ONE driver. For this method, the partition must include
        # one driver only.
        if method == 'BB':
            vehicle, shops_customers = partition
            # Compute the shortest path for this driver as it is used later.
            start_v, end_v = vehicle
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
                        route = partial_path.transform_to_actual_path()
                        cost = partial_path.dist
        else:
            raise NotImplementedError
        return route, cost

    def _compute_regions(self, path, dist, fraction_sd=.5, excluded_customers=None):
        customers = set(self._customers)
        if excluded_customers is not None:
            customers = customers.difference(excluded_customers)
        # Explore from each intermediate vertex in the path up to [dist] * [fraction_sd]
        # Find shops and customers within those explored regions.
        regions = {}  # Customers and shops by intermediate vertex.
        shops_region_revised = dict()
        for i, vertex in enumerate(path):
            # Explore graph from each intermediate vertex in driver's shortest path until 1/2 shortest distance.
            region = self._graph.explore_upto(vertex, dist * fraction_sd)
            # Which customers are in this region?
            # customers_region = self._customers.intersection(region.keys())
            customers_region = customers.intersection(region.keys())
            # Which shops are in this region?
            shops_region = self._shops.intersection(region.keys())
            # Which of those customers can be attended?
            # They are going to be the ones who have at least one of their preferred shops within the same region or
            # within a previous region.
            customers_region_revised = set()
            shops_region_revised[vertex] = set()
            for customer_region in customers_region:
                shops_customer = self._shops_by_group_id[self._customers_dict[customer_region]]
                # Check within this region.
                temp = shops_region.intersection(shops_customer)
                if temp:
                    customers_region_revised.add(customer_region)
                    shops_region_revised[vertex].update(temp)
                # else:  # Otherwise, check in previous regions.
                # Check in previous regions, too.
                for j in range(i - 1, -1, -1):
                    previous_vertex = path[j]
                    shops_past_region = regions[previous_vertex]['shops']
                    temp = shops_past_region.intersection(shops_customer)
                    if temp:
                        customers_region_revised.add(customer_region)
                        shops_region_revised[previous_vertex].update(temp)
                        # A break would've been efficient but it incorrectly could prevent shops in previous
                        # regions to be included in the search space. Of course, the inclusion of the customer
                        # into the set is not needed but luckily nothing happens as it is a set.
            # Gather customers and shops and classify them by intermediate vertex.
            regions[vertex] = {'customers': customers_region_revised, 'shops': shops_region}
        # Update regions with shops that may serve customers, i.e., there might be shops within regions that are not
        # used at all.
        for vertex in path:
            regions[vertex]['shops'] = shops_region_revised[vertex]
        return regions

    def _build_routes_milp(self):
        routes = list()
        for (i, j, _), variable in self.x.iteritems():
            if variable.solution_value():
                self._graph.compute_dist_paths([i], [j], recompute=True)
                routes.append(self._graph.paths[tuple(sorted([i, j]))])
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
            for variable in vars_:
                try:
                    coeff = c.GetCoefficient(variable)
                    if coeff > 0:
                        cs += "+ " + str(coeff) + " " + variable.name() + " "
                    elif coeff < 0:
                        cs += "- " + str(abs(coeff)) + " " + variable.name() + " "
                except KeyError:
                    pass
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
    _graph = Digraph()
    _shops_dict = dict()  # Shop with corresponding group ID.
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
        :param origin:
            Where the Hamiltonian path starts from.
        :param destination:
            Where the Hamiltonian path finishes.
        :param threshold:
            Upper bound for the Hamiltonian path's distance.
        :return:
        """
        PartialPath._graph = graph
        PartialPath._shops_dict = shops_dict
        PartialPath._origin = origin
        PartialPath._destination = destination
        PartialPath._threshold = threshold

        # Populate auxiliary shops and customers dictionaries indexed by group ID.
        PartialPath._shops_by_group_id = dict()
        PartialPath._customers_by_group_id = dict()
        for shop, group_id in shops_dict.iteritems():
            try:
                PartialPath._shops_by_group_id[group_id].add(shop)
            except KeyError:
                PartialPath._shops_by_group_id[group_id] = {shop}
        for customer, group_id in customers_dict.iteritems():
            try:
                PartialPath._customers_by_group_id[group_id].add(customer)
            except KeyError:
                PartialPath._customers_by_group_id[group_id] = {customer}

        # Populate shops, customers and groups sets for faster search.
        PartialPath._shops_set = set(shops_dict.keys())
        PartialPath._customers_set = set(customers_dict.keys())
        PartialPath._groups_set = \
            set(PartialPath._shops_by_group_id.keys()).intersection(PartialPath._customers_by_group_id.keys())

        # Create the initial paths. There is more than one tree in the branch and bound optimization process since the
        # pickup points are mutually exclusive within each group. Therefore, there are as many trees as the sum over all
        # shops where, for each shop, the number of trees is the number of combinations of shops from different groups.
        initial_paths = []
        # The initial paths all start from the origin and go to a shop.
        for shop, group_id in shops_dict.iteritems():
            # For each shop, the shops from the other groups are retrieved as we need the combinations of them.
            other_group_ids = PartialPath._groups_set.difference([group_id])
            other_groups = [PartialPath._shops_by_group_id[gi] for gi in other_group_ids]
            # Compute the combinations of shops where each combination has a shop from each group.
            combs_shops = set(product(*other_groups))
            # Create the initial paths as such. Each path starts with the origin. The next vertex in the path is the
            # current shop.
            for comb_shops in combs_shops:
                path = PartialPath([PartialPath._origin], 0, comb_shops, customers_dict.keys())
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
        :param shops: iterable
            Shops that can be part of the path and are not in it yet.
        :param customers: iterable
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
        :param vertex:
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

        :param from_: character string
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

        :param from_: character string
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

    def transform_to_actual_path(self):
        pairs = list()
        for i in range(len(self.path) - 1):
            v = self.path[i]
            w = self.path[i + 1]
            pairs.append((v, w))
        PartialPath._graph.compute_dist_paths(pairs=pairs, recompute=True)
        actual_path = [PartialPath._origin]
        for i in range(len(self.path) - 1):
            v = self.path[i]
            w = self.path[i + 1]
            actual_path.extend(PartialPath._graph.paths[tuple(sorted([v, w]))][1:])
        return actual_path
