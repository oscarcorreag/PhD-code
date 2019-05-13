from digraph import Digraph
from ortools.linear_solver import pywraplp
from utils import id_generator
from itertools import product


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

        # Dictionary indexed by customer in order to retrieve shops that can provide the goods.
        self.N_cl_pl = dict()

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
            self.N_r_pl[req] = shops
            self.N_r_cl[req] = customer
            self.N_cl_pl[customer] = shops  # Shops by customer
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
            self.B[(start_v, k)] = self._solver.NumVar(self._V_tws[start_v][0], self._V_tws[start_v][1], 'B(%d, %d)' % (start_v, k))
            # self.B[(end_v, k)] = self.solver.NumVar(0.0, self.solver.infinity(), 'B(%d, %d)' % (end_v, k))
            self.B[(end_v, k)] = self._solver.NumVar(self._V_tws[end_v][0], self._V_tws[end_v][1], 'B(%d, %d)' % (end_v, k))
        # --------------------------------------------------------------------------------------------------------------
        # Auxiliary variables z := x(i, j, k) * B(i, k).
        # --------------------------------------------------------------------------------------------------------------
        for i, j, k in self.x:
            self.z[(i, j, k)] = self._solver.NumVar(0.0, self._solver.infinity(), 'z(%d, %d, %d)' % (i, j, k))

    def _define_one_vehicle_one_pickup_constraints(self):
        constraints = [0] * len(self._requests)
        for req, _ in enumerate(self._requests):
            shops = self.N_r_pl[req]
            constraints[req] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
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
                constraints[req * K + k] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
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
                constraints[ord_ * K + k] = self._solver.Constraint(0.0, 0.0, str(self._solver.NumConstraints()))
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
            constraints[k] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
            for j in self.N_pl:
                constraints[k].SetCoefficient(self.x[(start_v, j, k)], 1.0)
            constraints[k].SetCoefficient(self.x[(start_v, end_v, k)], 1.0)
            constraints[K + k] = self._solver.Constraint(1.0, 1.0, str(self._solver.NumConstraints()))
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
            constraints[ord_] = self._solver.Constraint(0.0, self._solver.infinity(), str(self._solver.NumConstraints()))
            constraints[ord_].SetCoefficient(self.x[(i, j, k)], M)
            constraints[ord_].SetCoefficient(self.z[(i, j, k)], -1.0)
            #
            constraints[X + ord_] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                            str(self._solver.NumConstraints()))
            constraints[X + ord_].SetCoefficient(self.B[(i, k)], 1.0)
            constraints[X + ord_].SetCoefficient(self.z[(i, j, k)], -1.0)
            #
            constraints[2 * X + ord_] = self._solver.Constraint(-M, self._solver.infinity(),
                                                                str(self._solver.NumConstraints()))
            constraints[2 * X + ord_].SetCoefficient(self.B[(i, k)], -1.0)
            constraints[2 * X + ord_].SetCoefficient(self.x[(i, j, k)], -M)
            constraints[2 * X + ord_].SetCoefficient(self.z[(i, j, k)], 1.0)
            #
            constraints[3 * X + ord_] = self._solver.Constraint(0.0, self._solver.infinity(),
                                                                str(self._solver.NumConstraints()))
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
                    constraints[cnt] = self._solver.Constraint(self._working_graph[i][customer], self._solver.infinity(),
                                                               str(self._solver.NumConstraints()))
                    constraints[cnt].SetCoefficient(self.B[(customer, k)], 1.0)
                    constraints[cnt].SetCoefficient(self.B[(i, k)], -1.0)
                    cnt += 1
        for k, ((start_v, _, _), (end_v, _, _)) in enumerate(self._vehicles):
            constraints[cnt] = self._solver.Constraint(self._working_graph[start_v][end_v], self._solver.infinity(),
                                                       str(self._solver.NumConstraints()))
            constraints[cnt].SetCoefficient(self.B[(end_v, k)], 1.0)
            constraints[cnt].SetCoefficient(self.B[(start_v, k)], -1.0)
            cnt += 1

    def _define_time_window_constraints(self):
        constraints = [0] * len(self._working_graph)
        for ord_, (i, e, l) in enumerate(self._V_tws):
            for k, _ in enumerate(self._vehicles):
                if (i, k) in self.B:
                    constraints[ord_] = self._solver.Constraint(e, l, str(self._solver.NumConstraints()))
                    constraints[ord_].SetCoefficient(self.B[(i, k)], 1.0)

    def _define_objective(self):
        objective = self._solver.Objective()
        for (i, j, _), x in self.x.iteritems():
            objective.SetCoefficient(x, self._working_graph[i][j])
        objective.SetMinimization()

    def solve(self, requests, vehicles, method="MILP", verbose=False):

        self._requests = requests
        self._vehicles = vehicles

        self._build_working_graph()

        if method == "MILP":
            return self._solve_milp(verbose)

        if method == "SP-Based":
            return self._sp_based()

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
            return self._build_routes_milp()
        return None

    def _sp_based(self):
        partitions = self._compute_partitions()
        # Solve each partition
        # for partition in partitions:

    def _compute_partitions(self, method='SP-based'):
        partitions = {}
        if method == 'SP-based':
            # TODO: In case there are overlapping between drivers' shortest paths regions, define strategy. For now, each partition corresponds to each driver's exploration regions.
            for (start_v, _, _), (end_v, _, _) in self._vehicles:
                vehicle = (start_v, end_v)
                partitions[(start_v, end_v)] = self._compute_regions(vehicle)
        return partitions

    # def _solve_partition(self, partition, method='BB'):
    #     if method == 'BB':


    # def _branch_bound(self, partition):
        # Compute distances for lower bounds.
        #

    def _compute_regions(self, vehicle):
        start_v, end_v = vehicle
        customers = set(self.N_cl)
        shops = set(self.N_pl)
        # Compute shortest path and distance.
        # Then, explore from each intermediate vertex in the path up to [shortest_distance] / 2.
        # Find shops and customers within those explored regions.
        regions = {}  # Customers and shops by intermediate vertex.
        self._graph.compute_dist_paths([start_v], [end_v], method='meet-in-the-middle', recompute=True)
        dist = self._graph.dist[(start_v, end_v)]
        path = self._graph.paths[(start_v, end_v)]
        shops_region_revised = dict()
        for i, vertex in enumerate(path):
            # Explore graph from each intermediate vertex in driver's shortest path until 1/2 shortest distance.
            region = self._graph.explore_upto(vertex, dist / 2.)
            # Which customers are in this region?
            customers_region = customers.intersection(region.keys())
            # Which shops are in this region?
            shops_region = shops.intersection(region.keys())
            # Which of those customers can be attended?
            customers_region_revised = set()
            shops_region_revised[vertex] = set()
            # They are going to be the ones who have at least one of their preferred shops within the same region or
            # within a previous region.
            for customer_region in customers_region:
                shops_customer = self.N_cl_pl[customer_region]  # Shops for this customer.
                # Check within this region.
                temp = shops_region.intersection(shops_customer)
                if temp:
                    customers_region_revised.add(customer_region)
                    shops_region_revised[vertex].update(temp)
                else:  # Otherwise, check in previous regions.
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
    # IMPORTANT: Assume the graph is DIRECTED.
    # TODO: Generalize to any kind, i.e, DIRECTED/UNDIRECTED.
    _graph = Digraph(undirected=False)
    _shops_dict = dict()             # Each shop is associated with the ID of the group to which it belongs.
    _customers_dict = dict()         # Each customer is associated with the ID of the group of shops that may serve him.
    _shops_set = set()
    _customers_set = set()
    _groups_set = set()
    _from_set = set()
    _shops_by_group_id = dict()      # Group ID with corresponding shops.
    _customers_by_group_id = dict()  # Group ID with corresponding customers.
    _origin = None
    _destination = None

    @staticmethod
    def init(graph, customers_by_shops, origin, destination):
        """
        Parameters
        ----------
        :param graph: Digraph
            Used to retrieve shortest distances. It may be updated by an instance which in turn may benefit others.
        :param customers_by_shops: dict
            Key is a tuple containing the shops to where a group of customers can go.
            Value is an iterable containing the customers who can be served by the shops in the key.
        :param origin:
            Where the Hamiltonian path starts from.
        :param destination:
            Where the Hamiltonian path finishes.
        :return:
        """
        PartialPath._graph.append_from_graph(graph)
        PartialPath._origin = origin
        PartialPath._destination = destination

        # Build complementary data structures to speed up lower bound computation.
        PartialPath._from_set.add(origin)
        for shops, customers in customers_by_shops.iteritems():
            group_id = id_generator()
            PartialPath._shops_by_group_id[group_id] = set(shops)
            PartialPath._customers_by_group_id[group_id] = set(customers)
            PartialPath._shops_set.update(shops)
            PartialPath._customers_set.update(customers)
            PartialPath._groups_set.add(group_id)
            PartialPath._from_set.update(shops)
            PartialPath._from_set.update(customers)
            PartialPath._shops_dict.update({shop: group_id for shop in shops})
            PartialPath._customers_dict.update({customer: group_id for customer in customers})

    def __init__(self, path=None, dist=0, lb=0, shops_lb=None):
        """
        Parameters
        ----------
        :param path: list
            It is specially useful when a partial path spawns offspring.
        :param dist: float
            Traveled distance.
        :param lb: float
            Lower bound.
        :param shops_lb: iterable
            Shops that were considered when the lower bound was computed. Each shop in this set serves a different group
            of customers. Remember that only one shop per group of customers can be part of the solution.
        """
        if shops_lb:
            self._shops_lb = set(shops_lb)
        else:
            self._shops_lb = set()
        if path:
            self._path = list(path)
            self._dist = dist
            self._lb = lb
        else:  # When a path is not given, it is initialized with the origin.
            self._path = list()
            self._append_vertex(PartialPath._origin)  # Compute lower bound, so no need of self._lb assignment.
            self._dist = 0

    @staticmethod
    def init_paths():
        """
        Create the initial paths. There is more than one tree in the branch and bound optimization process since the
        pickup points are mutually exclusive within each group. Therefore, there are as many trees as shops times the
        number of combinations of shops from different groups.

        :return: list
            Initial paths.
        """
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
                path = PartialPath([PartialPath._origin], 0, shops_lb=comb_shops)
                path._append_vertex(shop)
                initial_paths.append(path)
        return initial_paths

    def spawn(self):
        """
        Create offspring where each child is one of the possible candidate vertices to visit. It is important to that
        each child inherits the list of shops 'self._shops_lb' as they inform which shops where used to compute the
        parent's lower bound.

        :return: list
            Offspring.
        """
        offspring = []
        to_ = self._where_to(self._path[-1])
        for vertex in to_:
            child = PartialPath(self._path, self._dist, shops_lb=self._shops_lb)
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
        if not self._path:
            self._path = [vertex]
            self._dist = 0  # No distance when there is one vertex in the path.
        else:
            path_end = self._path[-1]
            PartialPath._graph.compute_dist_paths([path_end], [vertex], compute_paths=False)
            self._path.append(vertex)
            self._dist = self._dist + PartialPath._graph.dist[(path_end, vertex)]
        # In case the new vertex is a shop, remove it from the shops to be used when computing the lower bound.
        # IMPORTANT: This list has to be up-to-date and not to include any shop already visited.
        self._shops_lb.discard(vertex)
        # Update the lower bound.
        self._compute_lb()

    def _compute_lb(self):
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
                dist = PartialPath._graph.dist[(vertex, to_)]
                dist_row_wise.append(dist)
                try:
                    dist_col_wise[to_][vertex] = dist
                except KeyError:
                    dist_col_wise[to_] = {vertex: dist}
            mins_row_wise[vertex] = min(dist_row_wise)
        # The distances by destination are updated with the value after subtracting the minimum by row.
        # Then, the mimimum by column are also saved.
        mins_col_wise = list()
        for to_, vertices in dist_col_wise.iteritems():
            for vertex in vertices:
                dist_col_wise[to_][vertex] -= mins_row_wise[vertex]
            mins_col_wise.append(min(dist_col_wise[to_].values()))
        # The lower bound is the sum of the row- and column-wise minimum values and path distance so far.
        self._lb = sum(mins_row_wise.values()) + sum(mins_col_wise) + self._dist

    def _where_to(self, from_):
        """
        What are the possible next vertices to visit from a specific vertex?

        :param from_: character string
            Current vertex for which the possible vertices to visit after are computed.
        :return: set
            Vertices to visit.
        """
        to_ = set()
        visited_shops = PartialPath._shops_set.intersection(self._path)
        visited_groups = {PartialPath._shops_dict[visited_shop] for visited_shop in visited_shops}
        non_visited_groups = PartialPath._groups_set.difference(visited_groups)
        # Shops in non-visited groups.
        for non_visited_group in non_visited_groups:
            to_.update(PartialPath._shops_by_group_id[non_visited_group].intersection(self._shops_lb))
        # Non-visited customers in visited groups.
        for visited_group in visited_groups:
            to_.update(PartialPath._customers_by_group_id[visited_group].difference(self._path))
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
        # Non-visited customers.
        to_ = PartialPath._customers_set.difference(self._path)
        # Set of shops sent in instantiation time.
        # IMPORTANT: This list has to be up-to-date and not to include any shop already visited.
        to_.update(self._shops_lb)
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
        from_ = {self._path[-1]}
        # Non-visited customers.
        from_.update(PartialPath._customers_set.difference(self._path))
        # Set of shops sent in instantiation time.
        # IMPORTANT: This list has to be up-to-date and not to include any shop already visited.
        from_.update(self._shops_lb)
        return from_

