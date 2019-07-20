from unittest import TestCase
from graph import Graph
from csdp_ap import PartialPath


class TestPartialPath(TestCase):

    def setUp(self):
        # self.graph = Digraph(undirected=False)
        self.graph = Graph()

        self.graph.append_edge_2(('A', 'o'), weight=1.5)
        self.graph.append_edge_2(('A', 'H'), weight=4)
        self.graph.append_edge_2(('A', 'J'), weight=3.5)
        self.graph.append_edge_2(('A', 'K'), weight=4)

        self.graph.append_edge_2(('B', 'P1'), weight=2)
        self.graph.append_edge_2(('B', 'P2'), weight=6)
        self.graph.append_edge_2(('B', 'd'), weight=3.6)
        self.graph.append_edge_2(('B', 'I'), weight=0.5)
        self.graph.append_edge_2(('B', 'G'), weight=1)

        self.graph.append_edge_2(('C', 'K'), weight=1)
        self.graph.append_edge_2(('C', 'L'), weight=1)
        self.graph.append_edge_2(('C', 'P2'), weight=4.5)

        self.graph.append_edge_2(('d', 'I'), weight=3.5)
        self.graph.append_edge_2(('d', 'L'), weight=2)
        self.graph.append_edge_2(('d', 'P2'), weight=2.5)

        self.graph.append_edge_2(('E', 'P1'), weight=1)
        self.graph.append_edge_2(('E', 'P3'), weight=2.5)
        self.graph.append_edge_2(('E', 'F'), weight=1)
        self.graph.append_edge_2(('E', 'o'), weight=2)

        self.graph.append_edge_2(('F', 'P1'), weight=0.5)
        self.graph.append_edge_2(('F', 'H'), weight=0.5)
        self.graph.append_edge_2(('F', 'G'), weight=1)

        self.graph.append_edge_2(('G', 'P1'), weight=0.75)
        self.graph.append_edge_2(('G', 'I'), weight=0.75)

        self.graph.append_edge_2(('H', 'I'), weight=2)
        self.graph.append_edge_2(('H', 'J'), weight=1)
        self.graph.append_edge_2(('H', 'o'), weight=2.5)

        self.graph.append_edge_2(('I', 'J'), weight=1)
        self.graph.append_edge_2(('I', 'L'), weight=2)

        self.graph.append_edge_2(('J', 'K'), weight=1)

        self.graph.append_edge_2(('K', 'L'), weight=1)

        self.graph.append_edge_2(('P1', 'P2'), weight=6)
        self.graph.append_edge_2(('P1', 'P3'), weight=3.5)

        self.graph.append_edge_2(('o', 'P3'), weight=2)

        self.shops = {'P1': 1, 'P2': 2, 'P3': 2}
        self.customers = {'A': 1, 'B': 1, 'C': 2}

        self.initial_paths = {
            (tuple(ip.path), ip.dist_lb):
                ip for ip in PartialPath.init(self.graph, self.shops, self.customers, 'o', 'd')
        }

    def test_init(self):
        self.assertEquals(len(self.initial_paths), 4)
        self.assertIn((('o', 'P2'), 26.5), self.initial_paths)
        self.assertIn((('o', 'P3'), 17.0), self.initial_paths)
        self.assertIn((('o', 'P1'), 23.75), self.initial_paths)
        self.assertIn((('o', 'P1'), 18.25), self.initial_paths)

    def test_spawn(self):
        offspring = dict()
        for k, ip in self.initial_paths.iteritems():
            offspring[k] = ip.spawn()
        self.assertEquals(len(offspring[(('o', 'P2'), 26.5)]), 2)
        self.assertEquals(len(offspring[(('o', 'P3'), 17.0)]), 2)
        self.assertEquals(len(offspring[(('o', 'P1'), 23.75)]), 3)
        self.assertEquals(len(offspring[(('o', 'P1'), 18.25)]), 3)
        # offspring[(('o', 'P2'), 26.5)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P2'), 26.5)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P2', 'C'], 26.5), paths_lbs)
        self.assertIn((['o', 'P2', 'P1'], 29.75), paths_lbs)
        # offspring[(('o', 'P3'), 17.0)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P3'), 17.0)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P3', 'C'], 22.0), paths_lbs)
        self.assertIn((['o', 'P3', 'P1'], 20.25), paths_lbs)
        # offspring[(('o', 'P1'), 23.75)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P1'), 23.75)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P1', 'P2'], 26.5), paths_lbs)
        self.assertIn((['o', 'P1', 'A'], 25.0), paths_lbs)
        self.assertIn((['o', 'P1', 'B'], 23.75), paths_lbs)
        # offspring[(('o', 'P1'), 18.25)]
        paths_lbs = list()
        for initial_path in offspring[(('o', 'P1'), 18.25)]:
            paths_lbs.append((initial_path.path, initial_path.dist_lb))
        self.assertIn((['o', 'P1', 'A'], 22.75), paths_lbs)
        self.assertIn((['o', 'P1', 'P3'], 21.5), paths_lbs)
        self.assertIn((['o', 'P1', 'B'], 18.25), paths_lbs)

    def test__append_vertex(self):
        self.fail()

    def test__compute_dist_lb(self):
        self.fail()

    def test__compute_cust_ub(self):
        ellipse = self.graph.nodes_within_ellipse('o', 'd', 10)
        shops = dict()
        customers = dict()
        for v in ellipse.keys():
            if v in self.shops:
                shops[v] = self.shops[v]
            elif v in self.customers:
                customers[v] = self.customers[v]
        initial_paths = PartialPath.init(self.graph, shops, customers, 'o', 'd', 10)
        for initial_path in initial_paths:
            print initial_path.path
            print initial_path.cust_ub
        self.fail()

    def test__where_to(self):
        initial_path = self.initial_paths[(('o', 'P1'), 18.25)]
        to = initial_path._where_to('P1')
        self.assertSetEqual(to, {'A', 'P3', 'B'})

    def test__lb_where_to(self):
        initial_path = self.initial_paths[(('o', 'P1'), 18.25)]
        to = initial_path._lb_where_to('P1')
        self.assertSetEqual(to, {'A', 'P3', 'C', 'B'})

    def test__lb_from_where(self):
        initial_path = self.initial_paths[(('o', 'P1'), 18.25)]
        from_ = initial_path._lb_from_where()
        self.assertSetEqual(from_, {'A', 'P3', 'C', 'P1', 'B'})

