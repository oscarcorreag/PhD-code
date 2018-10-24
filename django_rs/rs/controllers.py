import numpy as np

import models
from exceptions import NotEnoughNodesException
from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator


class SessionController:

    def __init__(self):
        pass

    @staticmethod
    def active_exists():
        # Is there active sessions?
        queryset = models.Session.objects.filter(active=True)
        if queryset.exists():
            return True

    @staticmethod
    def __generate_graph(session, seed=None, delta_meters=5000):
        # Compute random bbox coordinates based on session's city.
        if seed is not None:
            np.random.seed(seed)
        bounds = models.CITY_BOUNDS[session.city]
        delta = delta_meters / 111111.
        min_lon = np.random.uniform(bounds[0], bounds[2] - delta)
        min_lat = np.random.uniform(bounds[1], bounds[3] - delta)
        max_lon = min_lon + delta
        max_lat = min_lat + delta
        # Generate network sample.
        osm = OsmManager()
        generator = SuitableNodeWeightGenerator()
        graph, hotspots, pois, _, _ = osm.generate_graph_for_bbox(min_lon,
                                                                  min_lat,
                                                                  max_lon,
                                                                  max_lat,
                                                                  generator)
        return graph, hotspots, pois

    @staticmethod
    def __bootstrap_users(session, graph, hotspots, pois, seed=None):
        # Group POIs by subtype (activity).
        pois_per_activity = dict()
        for p in pois:
            pois_per_activity.setdefault(graph[p][2]['subtype'], []).append(p)
        # Available nodes for users.
        free_nodes = set(graph.keys()).difference(hotspots).difference(pois)
        if len(free_nodes) < session.simulated_users:
            raise NotEnoughNodesException
        # Create queries.
        if seed is not None:
            np.random.seed(seed)
        queries = []
        occupied = set()
        nq = len(pois_per_activity.keys())
        nuq = session.simulated_users / nq
        for i, (activity, pois_) in enumerate(pois_per_activity.iteritems()):
            where = set(free_nodes).difference(occupied)
            nuq_ = nuq
            if i == nq - 1:
                nuq_ = session.simulated_users - (nq - 1) * nuq
            origins = np.random.choice(a=list(where), size=nuq_, replace=False)
            queries.append((origins, pois_, activity))
            occupied.update(origins)
        return queries

    @staticmethod
    def prepare_new(session, seed=None):
        graph_model = list()
        pois_model = list()
        hotspots_model = list()
        users_model = list()
        # Generate graph associated with session.
        graph, hotspots, pois = SessionController.__generate_graph(session, seed=seed)
        # Create SessionGraph objects.
        for (i, j), weight in graph.get_edges().iteritems():
            graph_model.append(models.SessionGraph(edge_i=i, edge_j=j, weight=weight))
        # Create SessionGraphHotspot objects.
        for hotspot in hotspots:
            hotspots_model.append(models.SessionGraphHotspot(hotspot=hotspot))
        # Bootstrap simulated users.
        queries = SessionController.__bootstrap_users(session, graph, hotspots, pois)
        for origins, pois_, activity in queries:
            # Create SessionUser objects.
            for origin in origins:
                users_model.append(models.SessionUser(origin=origin, activity=activity))
            # Create SessionGraphPoi objects.
            for poi in pois_:
                pois_model.append(models.SessionGraphPoi(poi=poi, activity=activity))
        return graph_model, pois_model, hotspots_model, users_model
