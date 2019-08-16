from unittest import TestCase

import utils


class TestUtils(TestCase):
    def test_distribute_pois_in_queries(self):
        ppq = utils.distribute_pois_in_queries((10, 10), 8, 2, seed=0)
        self.assertDictEqual(ppq,
                             {0: [47, 77], 1: [59, 85], 2: [10, 89], 3: [35, 56], 4: [36, 28], 5: [88, 69], 6: [61, 78],
                              7: [65, 67]}
                             )

