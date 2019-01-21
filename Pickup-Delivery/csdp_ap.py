from digraph import Digraph
from ortools.linear_solver import pywraplp


class CsdpAp:
    def __init__(self, graph):
        self._graph = Digraph(undirected=False)
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
        self.N_pl = list()
        self.N_cl = list()
        self.N_r_pl = dict()
        self.N_r_cl = dict()
        self.N = list()
        self.M_s = list()
        self.M_e = list()
        self.M = list()
        self._V_tws = dict()  # All vertices each with its time window.
        # --------------------------------------------------------------------------------------------------------------
        # MILP
        # --------------------------------------------------------------------------------------------------------------
        self.solver = pywraplp.Solver("SolveIntegerProblem", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
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
            self.N_r_pl[req] = shops
            self.N_r_cl[req] = customer
            self.N_pl.extend(shops)
            self.N_cl.append(customer)
            self._V_tws[customer] = (e_c, l_c)
        self.N.extend(self.N_pl)
        self.N.extend(self.N_cl)
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
            for j in self.N_pl:
                self.A1.append((i, j))
        # Arc subset A2: Between pick-up locations from different requests.
        for req_i, shops_i in self.N_r_pl.iteritems():
            for req_j, shops_j in self.N_r_pl.iteritems():
                if req_i != req_j:
                    for i in shops_i:
                        for j in shops_j:
                            self.A2.append((i, j))
        # Arc subset A3: From each pick-up location to each on-line customer location.
        for i in self.N_pl:
            for j in self.N_cl:
                self.A3.append((i, j))
        # Arc subset A4: From each on-line customer location to pick-up locations of a different request.
        for req_i, i in self.N_r_cl.iteritems():
            for req_j, shops_j in self.N_r_pl.iteritems():
                if req_i != req_j:
                    for j in shops_j:
                        self.A4.append((i, j))
        # Arc subset A5: Between on-line customer locations.
        for i in self.N_cl:
            for j in self.N_cl:
                if i != j:
                    self.A5.append((i, j))
        # Arc subset A6: From each on-line customer location to each vehicle end location.
        for i in self.N_cl:
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
                    self.x[(i, j, k)] = self.solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # These variables are defined over A2 U A3 U A4 U A5.
        A_ = list()
        A_.extend(self.A2)
        A_.extend(self.A3)
        A_.extend(self.A4)
        A_.extend(self.A5)
        for i, j in A_:
            for k, _ in enumerate(self._vehicles):
                self.x[(i, j, k)] = self.solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # These variables are defined over a subset of A6. Defining a x(i, j, k) for which j != k^- does not make sense.
        for i, j in self.A6:
            for k, (_, (end_v, _, _)) in enumerate(self._vehicles):
                if j == end_v:
                    self.x[(i, j, k)] = self.solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # These variables are defined over a subset of A7. Defining a x(i, j, k) for which i != k^+ or j != k^- does not
        # make sense. However, validating i and j is not needed as arcs {(i, j) : i = k^+ and j != k^-} are not created.
        for i, j in self.A7:
            for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
                if i == start_v and j == end_v:
                    self.x[(i, j, k)] = self.solver.BoolVar("x(%d, %d, %d)" % (i, j, k))
        # --------------------------------------------------------------------------------------------------------------
        # Time variables at which vehicles start servicing at nodes.
        # Time window constraints are defined implicitly.
        # --------------------------------------------------------------------------------------------------------------
        for i in self.N:
            for k, _ in enumerate(self._vehicles):
                # self.B[(i, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (i, k))
                self.B[(i, k)] = self.solver.NumVar(self._V_tws[i][0], self._V_tws[i][1], 'B(%d, %d)' % (i, k))
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            # self.B[(start_v, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (start_v, k))
            self.B[(start_v, k)] = self.solver.NumVar(self._V_tws[start_v][0], self._V_tws[start_v][1], 'B(%d, %d)' % (start_v, k))
            # self.B[(end_v, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (end_v, k))
            self.B[(end_v, k)] = self.solver.NumVar(self._V_tws[end_v][0], self._V_tws[end_v][1], 'B(%d, %d)' % (end_v, k))
        # --------------------------------------------------------------------------------------------------------------
        # Auxiliary variables z := x(i, j, k) * B(i, k).
        # --------------------------------------------------------------------------------------------------------------
        for i, j, k in self.x:
            self.z[(i, j, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'z(%d, %d, %d)' % (i, j, k))

    def _define_one_vehicle_one_pickup_constraints(self):
        constraints = [0] * len(self._requests)
        for req, _ in enumerate(self._requests):
            shops = self.N_r_pl[req]
            constraints[req] = self.solver.Constraint(1.0, 1.0, str(self.solver.NumConstraints()))
            for k, _ in enumerate(self._vehicles):
                for i in shops:
                    for j, _ in self._working_graph[i].iteritems():
                        constraints[req].SetCoefficient(self.x[(i, j, k)], 1.0)

    def _define_same_vehicle_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * len(self._requests) * K
        for req, _ in enumerate(self._requests):
            shops = self.N_r_pl[req]
            customer = self.N_r_cl[req]
            for k, _ in enumerate(self._vehicles):
                constraints[req * K + k] = self.solver.Constraint(0.0, 0.0, str(self.solver.NumConstraints()))
                for i in shops:
                    for j, _ in self._working_graph[i].iteritems():
                        constraints[req * K + k].SetCoefficient(self.x[(i, j, k)], 1.0)
                for j in self.N:  # [N = (only possible) origins] TO customers.
                    if j != customer:
                        constraints[req * K + k].SetCoefficient(self.x[(j, customer, k)], -1.0)

    def _define_flow_conservation_locations_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * len(self.N) * K
        for ord_, i in enumerate(self.N):
            for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
                constraints[ord_ * K + k] = self.solver.Constraint(0.0, 0.0, str(self.solver.NumConstraints()))
                for j in self.N:
                    try:
                        constraints[ord_ * K + k].SetCoefficient(self.x[(j, i, k)], 1.0)
                    except KeyError:
                        pass
                    try:
                        constraints[ord_ * K + k].SetCoefficient(self.x[(i, j, k)], -1.0)
                    except KeyError:
                        pass
                try:
                    constraints[ord_ * K + k].SetCoefficient(self.x[(start_v, i, k)], 1.0)
                except KeyError:
                    pass
                try:
                    constraints[ord_ * K + k].SetCoefficient(self.x[(i, end_v, k)], -1.0)
                except KeyError:
                    pass

    def _define_flow_conservation_vehicle_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * 2 * K
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            constraints[k] = self.solver.Constraint(1.0, 1.0, str(self.solver.NumConstraints()))
            for j in self.N_pl:
                constraints[k].SetCoefficient(self.x[(start_v, j, k)], 1.0)
            constraints[k].SetCoefficient(self.x[(start_v, end_v, k)], 1.0)
            constraints[K + k] = self.solver.Constraint(1.0, 1.0, str(self.solver.NumConstraints()))
            for j in self.N_cl:
                constraints[K + k].SetCoefficient(self.x[(j, end_v, k)], 1.0)
            constraints[K + k].SetCoefficient(self.x[(start_v, end_v, k)], 1.0)

    def _define_time_consistency_constraints(self):
        # M = float(sys.maxint)
        # TODO: Confirm this:
        # Upper bound for start service time is the sum of the times of all arcs.
        M = sum(self._working_graph.get_edges().values())
        X = len(self.x)
        constraints = [0] * X * 4
        for ord_, (i, j, k) in enumerate(self.x):
            #
            constraints[ord_] = self.solver.Constraint(0.0, self.solver.infinity(), str(self.solver.NumConstraints()))
            constraints[ord_].SetCoefficient(self.x[(i, j, k)], M)
            constraints[ord_].SetCoefficient(self.z[(i, j, k)], -1.0)
            #
            constraints[X + ord_] = self.solver.Constraint(0.0, self.solver.infinity(),
                                                           str(self.solver.NumConstraints()))
            constraints[X + ord_].SetCoefficient(self.B[(i, k)], 1.0)
            constraints[X + ord_].SetCoefficient(self.z[(i, j, k)], -1.0)
            #
            constraints[2 * X + ord_] = self.solver.Constraint(-M, self.solver.infinity(),
                                                               str(self.solver.NumConstraints()))
            constraints[2 * X + ord_].SetCoefficient(self.B[(i, k)], -1.0)
            constraints[2 * X + ord_].SetCoefficient(self.x[(i, j, k)], -M)
            constraints[2 * X + ord_].SetCoefficient(self.z[(i, j, k)], 1.0)
            #
            constraints[3 * X + ord_] = self.solver.Constraint(0.0, self.solver.infinity(),
                                                               str(self.solver.NumConstraints()))
            constraints[3 * X + ord_].SetCoefficient(self.B[(j, k)], 1.0)
            constraints[3 * X + ord_].SetCoefficient(self.x[(i, j, k)], -self._working_graph[i][j])
            constraints[3 * X + ord_].SetCoefficient(self.z[(i, j, k)], -1.0)

    def _define_precedence_constraints(self):
        K = len(self._vehicles)
        constraints = [0] * ((len(self.N_pl) + 1) * K)
        cnt = 0
        for req, _ in enumerate(self._requests):
            shops = self.N_r_pl[req]
            customer = self.N_r_cl[req]
            for k, _ in enumerate(self._vehicles):
                for i in shops:
                    constraints[cnt] = self.solver.Constraint(self._working_graph[i][customer], self.solver.infinity(),
                                                              str(self.solver.NumConstraints()))
                    constraints[cnt].SetCoefficient(self.B[(customer, k)], 1.0)
                    constraints[cnt].SetCoefficient(self.B[(i, k)], -1.0)
                    cnt += 1
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            constraints[cnt] = self.solver.Constraint(self._working_graph[start_v][end_v], self.solver.infinity(),
                                                      str(self.solver.NumConstraints()))
            constraints[cnt].SetCoefficient(self.B[(end_v, k)], 1.0)
            constraints[cnt].SetCoefficient(self.B[(start_v, k)], -1.0)
            cnt += 1

    def _define_time_window_constraints(self):
        constraints = [0] * len(self._working_graph)
        for ord_, (i, e, l) in enumerate(self._V_tws):
            for k, _ in enumerate(self._vehicles):
                if (i, k) in self.B:
                    constraints[ord_] = self.solver.Constraint(e, l, str(self.solver.NumConstraints()))
                    constraints[ord_].SetCoefficient(self.B[(i, k)], 1.0)

    def _define_objective(self):
        objective = self.solver.Objective()
        for (i, j, _), x in self.x.iteritems():
            objective.SetCoefficient(x, self._working_graph[i][j])
        objective.SetMinimization()

    def routes(self, requests, vehicles, method="MILP", verbose=False):

        self._requests = requests
        self._vehicles = vehicles

        self._build_working_graph()

        if method == "MILP":
            return self._solve_milp(verbose)

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
        result_status = self.solver.Solve()
        # The problem has an optimal solution.
        # assert result_status == pywraplp.Solver.OPTIMAL
        # The solution looks legit (when using solvers other than
        # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
        assert self.solver.VerifySolution(1e-7, True)
        if result_status == pywraplp.Solver.OPTIMAL:
            # If verbose...
            if verbose:
                print('Number of variables =', self.solver.NumVariables())
                print('Number of constraints =', self.solver.NumConstraints())
                print('Optimal objective value = %d' % self.solver.Objective().Value())
                # Variables
                for _, variable in self.x.iteritems():
                    print('%s = %d' % (variable.name(), variable.solution_value()))
                for _, variable in self.B.iteritems():
                    print('%s = %d' % (variable.name(), variable.solution_value()))
                for _, variable in self.z.iteritems():
                    print('%s = %d' % (variable.name(), variable.solution_value()))
            # Return routes
            return self._build_routes_milp()
        return None

    def _build_routes_milp(self):
        routes = Digraph()
        for (i, j, _), variable in self.x.iteritems():
            if variable.solution_value():
                self._graph.compute_dist_paths([i], [j], recompute=True)
                routes.append_from_path(self._graph.paths[(i, j)], self._graph)
        return routes

    def print_milp_constraints(self):
        vars_ = list()
        vars_.extend(self.x.values())
        vars_.extend(self.B.values())
        vars_.extend(self.z.values())
        for nc in range(self.solver.NumConstraints()):
            c = self.solver.LookupConstraint(str(nc))
            cs = ""
            if c.lb() != c.ub() and c.lb() > -self.solver.infinity():
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
            if c.lb() != c.ub() and c.ub() < self.solver.infinity():
                cs += "<= " + str(c.ub())
            elif c.lb() == c.ub():
                cs += "= " + str(c.ub())
            print cs
