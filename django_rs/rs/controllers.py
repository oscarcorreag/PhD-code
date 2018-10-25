import numpy as np

import models
from exceptions import NoAvailableNodesException, NoHotspotsException, NoPoisException
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
    def __generate_graph(city, seed=None, delta_meters=5000):
        # Compute random bbox coordinates based on session's city.
        if seed is not None:
            np.random.seed(seed)
        bounds = models.CITY_BOUNDS[city]
        delta = delta_meters / 111111.
        min_lon = np.random.uniform(bounds[0], bounds[2] - delta)
        min_lat = np.random.uniform(bounds[1], bounds[3] - delta)
        max_lon = min_lon + delta
        max_lat = min_lat + delta
        # Generate network sample.
        osm = OsmManager()
        generator = SuitableNodeWeightGenerator()
        graph, hotspots, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator)
        return graph, hotspots, pois, min_lon, min_lat, max_lon, max_lat

    @staticmethod
    def __simulate_queries(how_many, graph, available, pois, seed=None):
        # Group POIs by subtype (activity).
        pois_per_activity = dict()
        for p in pois:
            pois_per_activity.setdefault(graph[p][2]['subtype'], []).append(p)
        # Create queries.
        if seed is not None:
            np.random.seed(seed)
        queries = []
        occupied = set()
        nq = len(pois_per_activity.keys())
        nuq = how_many / nq
        for i, (activity, pois_) in enumerate(pois_per_activity.iteritems()):
            where = set(available).difference(occupied)
            nuq_ = nuq
            if i == nq - 1:
                nuq_ = how_many - (nq - 1) * nuq
            origins = np.random.choice(a=list(where), size=nuq_, replace=False)
            queries.append((origins, pois_, activity))
            occupied.update(origins)
        return queries

    @staticmethod
    def prepare_new(simulated_users, city, seed=None):
        edges = list()
        nodes = list()
        users = list()
        activities = list()
        # Generate graph associated with session.
        graph, hotspots, pois, min_lon, min_lat, max_lon, max_lat = SessionController.__generate_graph(city, seed=seed)
        # Are there hot-spots, POIs?
        if not hotspots:
            raise NoHotspotsException
        if not pois:
            raise NoPoisException
        # Are there available nodes for users? (take into account creator)
        available = set(graph.keys()).difference(hotspots).difference(pois)
        if len(available) < simulated_users + 1:
            raise NoAvailableNodesException
        # Choose a random origin for creator.
        np.random.seed(seed)
        origin_creator = np.random.choice(a=list(available), size=1, replace=False)[0]
        available.remove(origin_creator)
        # Create SessionGraphEdge objects.
        for (i, j), weight in graph.get_edges().iteritems():
            edges.append(models.SessionGraphEdge(node_i=i, node_j=j, weight=weight))
        # Create SessionGraphNode objects.
        for hotspot in hotspots:
            nodes.append(models.SessionGraphNode(node=hotspot, node_type='H'))
        for node in available:
            nodes.append(models.SessionGraphNode(node=node, node_type='N'))
        # Simulate queries
        queries = SessionController.__simulate_queries(simulated_users, graph, available, pois)
        for origins, pois_, activity in queries:
            # Create SessionUser objects.
            for origin in origins:
                users.append(models.SessionUser(origin=origin, activity=activity))
            # Append POIs to SessionGraphNode objects.
            for poi in pois_:
                nodes.append(models.SessionGraphNode(node=poi, node_type='P', activity=activity))
            # Create SessionActivity objects.
            activities.append(models.SessionActivity(activity=activity))
        # return session, edges, nodes, users, activities
        return edges, nodes, users, activities, min_lon, min_lat, max_lon, max_lat, origin_creator
