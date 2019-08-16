from unittest import TestCase
from osmmanager import OsmManager


class TestOsmManager(TestCase):

    def setUp(self):
        self.osmmgr = OsmManager()
        self.bbox = (144.942043, -37.822496, 145.053342, -37.734496)

    def test_zonify_bbox(self):
        zones = self.osmmgr.zipf_sample_bbox(self.bbox, 500, hotspots=False, seed=0)
        print zones
        self.fail()
