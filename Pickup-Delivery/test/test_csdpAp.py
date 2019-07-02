from unittest import TestCase
from grid_digraph_generator import GridDigraphGenerator
from digraph import Digraph
from csdp_ap import CsdpAp, sample


class TestCsdpAp(TestCase):

    def setUp(self):
        generator = GridDigraphGenerator()
        self.graph = generator.generate(30, 30, edge_weighted=True)

    def test_solve(self):
        csdp_ap = CsdpAp(self.graph)
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # DETERMINISTIC REQUESTS
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        rs = [
            ([(691, 1, 300), (603, 1, 300)], (398, 1, 300)),
            ([(718, 1, 300)], (445, 1, 300)),
            ([(718, 1, 300)], (576, 1, 300)),
        ]
        #
        ds = [((549, 1, 300), (535, 1, 300))]
        # --------------------------------------------------------------------------------------------------------------
        # MILP
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds)
        self.assertAlmostEqual(cost, 27.970369551096667, 2)
        self.assertListEqual(routes,
                             [[549, 579, 580, 581, 582, 583, 584, 585, 586, 616, 617, 618, 619, 620, 590, 591, 592, 622,
                               623, 653, 654, 655, 625, 626, 627, 657, 658, 659, 689, 719, 718, 719, 689, 659, 658, 657,
                               627, 626, 625, 655, 654, 653, 623, 622, 592, 591, 590, 620, 619, 618, 617, 616, 586, 585,
                               584, 583, 582, 581, 580, 579, 578, 577, 576, 575, 574, 573, 603, 573, 574, 575, 545, 546,
                               547, 517, 518, 519, 489, 459, 429, 399, 398, 399, 400, 401, 371, 372, 373, 374, 375, 376,
                               406, 407, 377, 378, 379, 380, 381, 411, 412, 413, 414, 415, 445, 444, 474, 504, 534,
                               535]])
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=0.5)
        self.assertAlmostEqual(cost, 30.133139017410407, 2)
        self.assertListEqual(routes,
                             [[549, 579, 580, 581, 582, 583, 584, 585, 586, 616, 617, 618, 619, 620, 590, 591, 592, 622,
                               623, 653, 654, 655, 625, 626, 627, 657, 658, 659, 689, 719, 718, 719, 689, 659, 658, 657,
                               627, 626, 625, 655, 654, 653, 623, 622, 592, 591, 590, 620, 619, 618, 617, 616, 586, 585,
                               584, 583, 582, 581, 580, 579, 578, 577, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585,
                               586, 556, 526, 527, 528, 529, 530, 531, 532, 533, 503, 473, 474, 444, 445, 444, 474, 504,
                               534, 535],
                              [603, 573, 574, 575, 545, 546, 547, 517, 518, 519, 489, 459, 429, 399, 398, 399, 429, 459,
                               489, 519, 518, 517, 547, 546, 545, 575, 574, 573, 603]])
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-Voronoi'
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
        self.assertAlmostEquals(cost, 27.970369551096667, 2)
        self.assertListEqual(routes,
                             [[549, 579, 580, 581, 582, 583, 584, 585, 586, 616, 617, 618, 619, 620, 590, 591, 592, 622,
                               623, 653, 654, 655, 625, 626, 627, 657, 658, 659, 689, 719, 718, 719, 689, 659, 658, 657,
                               627, 626, 625, 655, 654, 653, 623, 622, 592, 591, 590, 620, 619, 618, 617, 616, 586, 585,
                               584, 583, 582, 581, 580, 579, 578, 577, 576, 575, 574, 573, 603, 573, 574, 575, 545, 546,
                               547, 517, 518, 519, 489, 459, 429, 399, 398, 399, 400, 401, 371, 372, 373, 374, 375, 376,
                               406, 407, 377, 378, 379, 380, 381, 411, 412, 413, 414, 415, 445, 444, 474, 504, 534,
                               535]])
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # RANDOM REQUESTS
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        rs, ss, cs, ds = sample(nc=10, ng=3, min_s=5, max_s=10, nv=4, vertices=self.graph.keys(), seed=0)
        # --------------------------------------------------------------------------------------------------------------
        # MILP
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds)
        self.assertAlmostEquals(cost, 41.64575461140621, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=0.5)
        self.assertAlmostEquals(cost, 41.645754611406204, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-Voronoi'
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
        self.assertAlmostEquals(cost, 63.13778937426519, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        # --------------------------------------------------------------------------------------------------------------
        # Compute drivers' shortest paths to validate thresholds.
        # --------------------------------------------------------------------------------------------------------------
        pairs = list()
        for driver in ds:
            pairs.append((driver[0][0], driver[1][0]))
        self.graph.compute_dist_paths(pairs=pairs, compute_paths=False)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-threshold' -> threshold_sd=1.5
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold')
        self.assertAlmostEquals(cost, 55.132556063790524, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        self.assert_individual_costs_threshold(1.5, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-threshold' -> threshold_sd=1.6
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.6)
        self.assertAlmostEquals(cost, 51.19801933262737, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        self.assert_individual_costs_threshold(1.6, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-threshold' -> threshold_sd=1.7
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.7)
        self.assertAlmostEquals(cost, 51.19801933262737, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        self.assert_individual_costs_threshold(1.7, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-threshold' -> threshold_sd=1.8
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.8)
        self.assertAlmostEquals(cost, 51.19801933262737, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        self.assert_individual_costs_threshold(1.8, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-threshold' -> threshold_sd=1.9
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.9)
        self.assertAlmostEquals(cost, 53.99520740933061, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        self.assert_individual_costs_threshold(1.9, routes)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition='SP-threshold' -> threshold_sd=2.0
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=2.0)
        self.assertAlmostEquals(cost, 56.4207354108783, 2)
        self.assert_total_cost_from_individual_routes(cost, routes)
        self.assert_individual_costs_threshold(2.0, routes)

    def compute_route_cost(self, route):
        route_graph = Digraph(undirected=False)
        route_graph.append_from_path(route, self.graph)
        return route_graph.compute_total_weights()[0]

    def assert_total_cost_from_individual_routes(self, cost, routes):
        total_cost = 0
        for route in routes:
            route_cost = self.compute_route_cost(route)
            total_cost += route_cost
        self.assertAlmostEqual(cost, total_cost, 4)

    def assert_individual_costs_threshold(self, threshold, routes):
        for route in routes:
            route_cost = self.compute_route_cost(route)
            origin = route[0]
            destination = route[-1]
            if origin == destination:
                continue
            threshold = self.graph.dist[tuple(sorted([origin, destination]))] * threshold
            self.assertLessEqual(route_cost, threshold)
