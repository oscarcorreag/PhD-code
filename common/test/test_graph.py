from unittest import TestCase
from grid_digraph_generator import GridDigraphGenerator


class TestGraph(TestCase):

    def setUp(self):
        generator = GridDigraphGenerator()
        self.graph = generator.generate(5, 5, edge_weighted=False)

    def test_clone_node(self):
        new_node = self.graph.clone_node(12)
        self.assertDictEqual(self.graph[12], self.graph[new_node])

    def test_get_k_closest_destinations(self):
        dist, paths = self.graph.get_k_closest_destinations(12, 3, [0, 1, 2, 3, 4])
        self.assertDictEqual(dist, {1: 3, 2: 2, 3: 3})
        self.assertDictEqual(paths, {1: [12, 7, 2, 1], 2: [12, 7, 2], 3: [12, 7, 2, 3]})

    def test_get_voronoi_paths_cells(self):
        # --------------------------------------------------------------------------------------------------------------
        # Paths DO NOT OVERLAP.
        # --------------------------------------------------------------------------------------------------------------
        paths = [[1, 2, 3, 4], [16, 17, 18, 19]]
        cells, paths_by_node = self.graph.get_voronoi_paths_cells(paths)
        self.assertDictEqual(cells,
                             {
                                 (16, 19): [16, 17, 18, 19, 11, 12, 13, 14, 15, 21, 22, 23, 24, 10, 20],
                                 (1, 4): [1, 2, 3, 4, 0, 6, 7, 8, 9, 5]
                             })
        self.assertDictEqual(paths_by_node,
                             {
                                 0: (1, 4),
                                 1: (1, 4),
                                 2: (1, 4),
                                 3: (1, 4),
                                 4: (1, 4),
                                 5: (1, 4),
                                 6: (1, 4),
                                 7: (1, 4),
                                 8: (1, 4),
                                 9: (1, 4),
                                 10: (16, 19),
                                 11: (16, 19),
                                 12: (16, 19),
                                 13: (16, 19),
                                 14: (16, 19),
                                 15: (16, 19),
                                 16: (16, 19),
                                 17: (16, 19),
                                 18: (16, 19),
                                 19: (16, 19),
                                 20: (16, 19),
                                 21: (16, 19),
                                 22: (16, 19),
                                 23: (16, 19),
                                 24: (16, 19)
                             })

        paths = [[1, 2, 3, 4], [16, 16]]
        cells, paths_by_node = self.graph.get_voronoi_paths_cells(paths)
        self.assertDictEqual(cells,
                             {(16, 16): [16, 11, 15, 17, 21, 10, 18, 20, 22, 23],
                              (1, 4): [1, 2, 3, 4, 0, 6, 7, 8, 9, 5, 12, 13, 14, 19, 24]})
        # --------------------------------------------------------------------------------------------------------------
        # Paths DO OVERLAP.
        # --------------------------------------------------------------------------------------------------------------
        paths = [[2, 7, 12, 17, 22], [10, 11, 12, 13, 14]]
        cells, paths_by_node = self.graph.get_voronoi_paths_cells(paths)
        self.assertDictEqual(cells,
                             {
                                 (2, 22): [2, 7, 17, 22, 1, 3, 6, 8, 21, 23, 0, 4],
                                 (10, 14): [10, 11, 12, 13, 14, 5, 9, 15, 16, 18, 19, 20, 24]
                             })
        self.assertDictEqual(paths_by_node,
                             {
                                 0: (2, 22),
                                 1: (2, 22),
                                 2: (2, 22),
                                 3: (2, 22),
                                 4: (2, 22),
                                 5: (10, 14),
                                 6: (2, 22),
                                 7: (2, 22),
                                 8: (2, 22),
                                 9: (10, 14),
                                 10: (10, 14),
                                 11: (10, 14),
                                 12: (10, 14),
                                 13: (10, 14),
                                 14: (10, 14),
                                 15: (10, 14),
                                 16: (10, 14),
                                 17: (2, 22),
                                 18: (10, 14),
                                 19: (10, 14),
                                 20: (10, 14),
                                 21: (2, 22),
                                 22: (2, 22),
                                 23: (2, 22),
                                 24: (10, 14)
                             })

    def test_nodes_within_ellipse(self):
        ellipse = self.graph.nodes_within_ellipse(11, 13, 4)
        self.assertDictEqual(ellipse,
                             {
                                 6: {11: 1, 13: 3},
                                 7: {11: 2, 13: 2},
                                 8: {11: 3, 13: 1},
                                 10: {11: 1, 13: 3},
                                 11: {11: 0, 13: 2},
                                 12: {11: 1, 13: 1},
                                 13: {11: 2, 13: 0},
                                 14: {11: 3, 13: 1},
                                 16: {11: 1, 13: 3},
                                 17: {11: 2, 13: 2},
                                 18: {11: 3, 13: 1}
                             })

    def test_compute_mst(self):
        mst = self.graph.compute_mst()
        self.assertDictEqual(mst,
                             {0: {1: 1, 5: 1}, 1: {0: 1, 2: 1, 6: 1}, 2: {1: 1, 3: 1, 7: 1}, 3: {8: 1, 2: 1, 4: 1},
                              4: {9: 1, 3: 1}, 5: {0: 1, 10: 1}, 6: {1: 1, 11: 1}, 7: {2: 1, 12: 1}, 8: {3: 1, 13: 1},
                              9: {4: 1, 14: 1}, 10: {5: 1, 15: 1}, 11: {16: 1, 6: 1}, 12: {17: 1, 7: 1},
                              13: {8: 1, 18: 1}, 14: {9: 1, 19: 1}, 15: {10: 1, 20: 1}, 16: {11: 1, 21: 1},
                              17: {12: 1, 22: 1}, 18: {13: 1, 23: 1}, 19: {24: 1, 14: 1}, 20: {15: 1}, 21: {16: 1},
                              22: {17: 1}, 23: {18: 1}, 24: {19: 1}})

    def test_extract_node_induced_subgraph(self):
        nodes = [6, 11, 12, 13, 24]
        subgraph = self.graph.extract_node_induced_subgraph(nodes)
        self.assertDictEqual(subgraph,
                             {24: {}, 11: {12: 1, 6: 1}, 12: {11: 1, 13: 1}, 13: {12: 1}, 6: {11: 1}})

    def test_build_metric_closure(self):
        nodes = [0, 4, 12, 20, 24]
        subgraph = self.graph.build_metric_closure(nodes)
        self.assertDictEqual(subgraph,
                             {0: {24: 8, 12: 4, 4: 4, 20: 4}, 12: {0: 4, 20: 4, 4: 4, 24: 4},
                              4: {0: 4, 20: 8, 12: 4, 24: 4}, 20: {0: 4, 12: 4, 4: 8, 24: 4},
                              24: {0: 8, 12: 4, 4: 4, 20: 4}})
        excluded_edges = [(24, 12)]
        subgraph = self.graph.build_metric_closure(nodes, excluded_edges=excluded_edges)
        self.assertDictEqual(subgraph,
                             {0: {24: 8, 12: 4, 4: 4, 20: 4}, 12: {0: 4, 20: 4, 4: 4}, 4: {0: 4, 20: 8, 12: 4, 24: 4},
                              20: {0: 4, 12: 4, 4: 8, 24: 4}, 24: {0: 8, 20: 4, 4: 4}})

    def test_compute_euler_tour(self):
        mst = self.graph.compute_mst()
        mst.complete_both_directions()
        euler_tour = mst.compute_euler_tour(24)
        self.assertListEqual(euler_tour,
                             [24, 19, 14, 9, 4, 3, 8, 13, 18, 23, 18, 13, 8, 3, 2, 1, 0, 5, 10, 15, 20, 15, 10, 5, 0, 1,
                              6, 11, 16, 21, 16, 11, 6, 1, 2, 7, 12, 17, 22, 17, 12, 7, 2, 3, 4, 9, 14, 19, 24]
                             )

    def test_complete_both_directions(self):
        mst = self.graph.compute_mst()
        self.assertDictEqual(mst.get_edges(),
                             {(11, 16): 1, (8, 13): 1, (15, 20): 1, (16, 21): 1, (10, 15): 1, (1, 6): 1, (1, 2): 1,
                              (4, 9): 1, (7, 12): 1, (12, 17): 1, (2, 7): 1, (9, 14): 1, (6, 11): 1, (19, 24): 1,
                              (17, 22): 1, (0, 1): 1, (5, 10): 1, (3, 4): 1, (0, 5): 1, (3, 8): 1, (18, 23): 1,
                              (13, 18): 1, (2, 3): 1, (14, 19): 1}
                             )
        mst.complete_both_directions()
        self.assertDictEqual(mst.get_edges(),
                             {(11, 16): 1, (8, 13): 1, (21, 16): 1, (15, 20): 1, (16, 21): 1, (18, 13): 1, (2, 1): 1,
                              (10, 15): 1, (3, 2): 1, (1, 6): 1, (9, 4): 1, (24, 19): 1, (14, 9): 1, (7, 2): 1,
                              (1, 2): 1, (4, 9): 1, (19, 14): 1, (7, 12): 1, (12, 17): 1, (5, 0): 1, (22, 17): 1,
                              (2, 7): 1, (16, 11): 1, (9, 14): 1, (17, 12): 1, (6, 11): 1, (12, 7): 1, (10, 5): 1,
                              (15, 10): 1, (19, 24): 1, (17, 22): 1, (13, 8): 1, (1, 0): 1, (0, 1): 1, (8, 3): 1,
                              (5, 10): 1, (3, 4): 1, (6, 1): 1, (0, 5): 1, (3, 8): 1, (18, 23): 1, (13, 18): 1,
                              (23, 18): 1, (4, 3): 1, (2, 3): 1, (20, 15): 1, (14, 19): 1, (11, 6): 1}
                             )
