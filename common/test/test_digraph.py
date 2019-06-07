from unittest import TestCase
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper


class TestDigraph(TestCase):
    def test_get_voronoi_paths_cells(self):
        generator = GridDigraphGenerator()
        graph = generator.generate(5, 5, edge_weighted=False)
        # --------------------------------------------------------------------------------------------------------------
        # Paths DO NOT OVERLAP.
        # --------------------------------------------------------------------------------------------------------------
        paths = [[1, 2, 3, 4], [16, 17, 18, 19]]
        cells, paths_by_node = graph.get_voronoi_paths_cells(paths)
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

        # --------------------------------------------------------------------------------------------------------------
        # Paths DO OVERLAP.
        # --------------------------------------------------------------------------------------------------------------
        paths = [[2, 7, 12, 17, 22], [10, 11, 12, 13, 14]]
        cells, paths_by_node = graph.get_voronoi_paths_cells(paths)
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
        generator = GridDigraphGenerator()
        graph = generator.generate(5, 5, edge_weighted=False)
        ellipse, _ = graph.nodes_within_ellipse(11, 13, 4)
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

    # def test_nodes_within_ellipse_opt(self):
    #     generator = GridDigraphGenerator()
    #     graph = generator.generate(50, 50)
    #     graph.compute_dist_paths(pairs=[(1260, 2060), (1260, 1359), (1359, 2060)], compute_paths=True)
    #     print graph.dist[(1260, 1359)], graph.dist[(1359, 2060)]
    #     print graph.paths[(1359, 2060)]
    #     helper = NetworkXGraphHelper(graph)
    #     sd = graph.dist[(1260, 2060)]
    #     constant = sd * 1.1
    #     ellipse_1, iterations_1 = graph.nodes_within_ellipse(1260, 2060, constant)
    #     helper.draw_graph(special_nodes=[(ellipse_1.keys(), None, 30)])
    #     ellipse_2, iterations_2 = graph.nodes_within_ellipse_opt(1260, 2060, constant)
    #     helper.draw_graph(special_nodes=[(ellipse_2.keys(), None, 30)])
    #     self.assertListEqual(sorted(ellipse_1.keys()), sorted(ellipse_2.keys()))
    #     self.assertGreater(iterations_1, iterations_2)
