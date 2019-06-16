from unittest import TestCase
from grid_digraph_generator import GridDigraphGenerator
from csdp_ap import CsdpAp, sample


class TestCsdpAp(TestCase):

    def test_solve(self):
        generator = GridDigraphGenerator()
        graph = generator.generate(30, 30, edge_weighted=False)
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
        vs = [((549, 1, 300), (535, 1, 300))]

        csdp_ap = CsdpAp(graph)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition=SD-fraction -> fraction=0.5
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, vs, method="SP-based", fraction_sd=0.5)
        self.assertEquals(cost, 41)
        self.assertListEqual(routes,
                             [
                                 [549, 548, 547, 546, 545, 544, 543, 573, 603, 573, 543, 513, 483, 453, 423, 393, 394,
                                  395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411,
                                  412, 413, 414, 415, 445, 475, 505, 535]
                             ])
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition=SP-Voronoi
        # --------------------------------------------------------------------------------------------------------------
        routes, cost = csdp_ap.solve(rs, vs, method="SP-based", partition_method='SP-Voronoi')
        self.assertEquals(cost, 85)
        self.assertListEqual(routes,
                             [[549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566,
                               567, 568, 598, 628, 658, 688, 718, 688, 658, 628, 627, 626, 625, 624, 623, 622, 621, 620,
                               619, 618, 617, 616, 615, 614, 613, 612, 611, 610, 609, 608, 607, 606, 605, 604, 603, 573,
                               574, 575, 576, 546, 516, 486, 456, 426, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405,
                               406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 445, 475, 505, 535]])
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # RANDOM REQUESTS
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        rs, ss, cs, vs = sample(nc=10, ng=3, min_s=5, max_s=10, nv=4, vertices=graph.keys(), seed=0)
        # --------------------------------------------------------------------------------------------------------------
        # SP-based -> Partition=SP-Voronoi
        # --------------------------------------------------------------------------------------------------------------
        _, cost = csdp_ap.solve(rs, vs, method="SP-based", partition_method='SP-Voronoi')
        self.assertEquals(cost, 162)


