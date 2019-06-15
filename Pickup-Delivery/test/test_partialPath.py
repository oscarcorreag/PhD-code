from unittest import TestCase
from digraph import Digraph
from csdp_ap import PartialPath


class TestPartialPath(TestCase):

    def setUp(self):
        self.graph = Digraph(undirected=False)

        self.graph.append_edge_2(('A', 'B'), weight=5)
        self.graph.append_edge_2(('A', 'C'), weight=6)
        self.graph.append_edge_2(('A', 'P2'), weight=9.5)
        self.graph.append_edge_2(('A', 'P3'), weight=3.5)
        self.graph.append_edge_2(('A', 'd'), weight=7)

        self.graph.append_edge_2(('B', 'A'), weight=5)
        self.graph.append_edge_2(('B', 'C'), weight=3.5)
        self.graph.append_edge_2(('B', 'P2'), weight=6)
        self.graph.append_edge_2(('B', 'P3'), weight=5.5)
        self.graph.append_edge_2(('B', 'd'), weight=3.6)

        self.graph.append_edge_2(('C', 'A'), weight=6)
        self.graph.append_edge_2(('C', 'B'), weight=3.5)
        self.graph.append_edge_2(('C', 'P1'), weight=4.5)
        self.graph.append_edge_2(('C', 'd'), weight=3)

        self.graph.append_edge_2(('P1', 'A'), weight=5)
        self.graph.append_edge_2(('P1', 'B'), weight=2)
        self.graph.append_edge_2(('P1', 'C'), weight=4.5)
        self.graph.append_edge_2(('P1', 'P2'), weight=6)
        self.graph.append_edge_2(('P1', 'P3'), weight=3.5)

        self.graph.append_edge_2(('P2', 'A'), weight=9.5)
        self.graph.append_edge_2(('P2', 'B'), weight=6)
        self.graph.append_edge_2(('P2', 'C'), weight=4.5)
        self.graph.append_edge_2(('P2', 'P1'), weight=6)

        self.graph.append_edge_2(('P3', 'A'), weight=3.5)
        self.graph.append_edge_2(('P3', 'B'), weight=5.5)
        self.graph.append_edge_2(('P3', 'C'), weight=6.5)
        self.graph.append_edge_2(('P3', 'P1'), weight=3.5)

        self.graph.append_edge_2(('o', 'P1'), weight=3)
        self.graph.append_edge_2(('o', 'P2'), weight=8)
        self.graph.append_edge_2(('o', 'P3'), weight=2)
        self.graph.append_edge_2(('o', 'd'), weight=8)

        self.shops = {'P1': 1, 'P2': 2, 'P3': 2}
        self.customers = {'A': 1, 'B': 1, 'C': 2}

        self.initial_paths = {
            (tuple(ip.path), ip.dist_lb):
                ip for ip in PartialPath.init(self.graph, self.shops, self.customers, 'o', 'd')
        }

    def test_init(self):
        self.assertEquals(len(self.initial_paths), 4)
        self.assertIn((('o', 'P2'), 29.0), self.initial_paths)
        self.assertIn((('o', 'P3'), 19.0), self.initial_paths)
        self.assertIn((('o', 'P1'), 25.0), self.initial_paths)
        self.assertIn((('o', 'P1'), 18.5), self.initial_paths)

    def test_spawn(self):
        offspring = dict()
        for k, ip in self.initial_paths.iteritems():
            offspring[k] = ip.spawn()
        self.assertEquals(len(offspring[(('o', 'P2'), 29.0)]), 2)
        self.assertEquals(len(offspring[(('o', 'P3'), 19.0)]), 2)
        self.assertEquals(len(offspring[(('o', 'P1'), 25.0)]), 3)
        self.assertEquals(len(offspring[(('o', 'P1'), 18.5)]), 3)
        # offspring[(('o', 'P2'), 29.0)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P2'), 29.0)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P2', 'C'], 29.0), paths_lbs)
        self.assertIn((['o', 'P2', 'P1'], 29.0), paths_lbs)
        # offspring[(('o', 'P3'), 19.0)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P3'), 19.0)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P3', 'C'], 25.0), paths_lbs)
        self.assertIn((['o', 'P3', 'P1'], 20.5), paths_lbs)
        # offspring[(('o', 'P1'), 25.0)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P1'), 25.0)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P1', 'P2'], 26.5), paths_lbs)
        self.assertIn((['o', 'P1', 'A'], 26.5), paths_lbs)
        self.assertIn((['o', 'P1', 'B'], 26.0), paths_lbs)
        # offspring[(('o', 'P1'), 18.5)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P1'), 18.5)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P1', 'A'], 23.5), paths_lbs)
        self.assertIn((['o', 'P1', 'P3'], 21.5), paths_lbs)
        self.assertIn((['o', 'P1', 'B'], 18.5), paths_lbs)

    def test__append_vertex(self):

        self.fail()

    def test__compute_dist_lb(self):
        self.fail()

    def test__compute_cust_ub(self):
        ellipse = self.graph.nodes_within_ellipse('o', 'd', 16)
        shops = dict()
        customers = dict()
        for v in ellipse.keys():
            if v in self.shops:
                shops[v] = self.shops[v]
            elif v in self.customers:
                customers[v] = self.customers[v]
        initial_paths = PartialPath.init(self.graph, shops, customers, 'o', 'd', 16)
        print initial_paths
        self.fail()

    def test__where_to(self):
        initial_path = self.initial_paths[(('o', 'P1'), 18.5)]
        to = initial_path._where_to('P1')
        self.assertSetEqual(to, {'A', 'P3', 'B'})

    def test__lb_where_to(self):
        initial_path = self.initial_paths[(('o', 'P1'), 18.5)]
        to = initial_path._lb_where_to('P1')
        self.assertSetEqual(to, {'A', 'P3', 'C', 'B'})

    def test__lb_from_where(self):
        initial_path = self.initial_paths[(('o', 'P1'), 18.5)]
        from_ = initial_path._lb_from_where()
        self.assertSetEqual(from_, {'A', 'P3', 'C', 'P1', 'B'})

