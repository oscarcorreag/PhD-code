# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
#
# from django.db import transaction
# from django.db.utils import DatabaseError
#
# from rest_framework import viewsets
#
# import models
# import serializers
# import exceptions
# import osmmanager
# import suitability
#
#
# # Create your views here.
# class SessionViewSet(viewsets.ModelViewSet):
#
#     queryset = models.Session.objects.all().order_by("-start_time")
#     serializer_class = serializers.SessionSerializer
#
#     @staticmethod
#     def active_session_exists():
#         # Is there active sessions?
#         active_session = None
#         try:
#             active_session = models.Session.objects.get(active=True)
#         except models.Session.DoesNotExist:
#             pass
#         return active_session
#
#     @staticmethod
#     def generate_graph(min_lon, min_lat, max_lon, max_lat, poi_names):
#         osm = osmmanager.OsmManager()
#         generator = suitability.SuitableNodeWeightGenerator()
#         graph, _, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator, hotspots=False, poi_names=poi_names)
#         return graph, _, pois
#
#     # @staticmethod
#     # def simulate_requests(poiname_customers, available):
#
#     @staticmethod
#     def prepare_new(min_lon, min_lat, max_lon, max_lat, poi_names):
#         edges = list()
#         nodes = list()
#         # Generate graph associated with session.
#         graph, _, pois = SessionViewSet.generate_graph(min_lon, min_lat, max_lon, max_lat, poi_names)
#         # Are there POIs?
#         if not pois:
#             raise exceptions.NoPoisException
#         # # Are there available nodes for users? (take into account creator)
#         # available = set(graph.keys()).difference(hotspots).difference(pois)
#         # if len(available) < simulated_users + 1:
#         #     raise exceptions.NoAvailableNodesException
#         # # Choose a random origin for creator.
#         # np.random.seed(seed)
#         # origin_creator = np.random.choice(a=list(available), size=1, replace=False)[0]
#         # available.remove(origin_creator)
#         # # Create SessionGraphEdge objects.
#         # for (i, j), weight in graph.get_edges().iteritems():
#         #     edges.append(models.SessionGraphEdge(node_i=i, node_j=j, weight=weight))
#         # # Create SessionGraphNode objects.
#         # for hotspot in hotspots:
#         #     nodes.append(models.SessionGraphNode(node=hotspot, node_type='H'))
#         # for node in available:
#         #     nodes.append(models.SessionGraphNode(node=node, node_type='N'))
#         # # Simulate queries
#         # queries = SessionViewSet.simulate_queries(simulated_users, graph, available, pois)
#         # for origins, pois_, activity in queries:
#         #     # Create SessionUser objects.
#         #     for origin in origins:
#         #         users.append(models.SessionUser(origin=origin, activity=activity))
#         #     # Append POIs to SessionGraphNode objects.
#         #     for poi in pois_:
#         #         nodes.append(models.SessionGraphNode(node=poi, node_type='P', activity=activity))
#         #     # Create SessionActivity objects.
#         #     activities.append(models.SessionActivity(activity=activity))
#         # # return session, edges, nodes, users, activities
#         # return edges, nodes, users, activities, min_lon, min_lat, max_lon, max_lat, origin_creator
#
#     def perform_create(self, serializer):
#         # Check whether an active session exists already.
#         if SessionViewSet.active_session_exists():
#             raise exceptions.ActiveSessionExistsException
#         # Prepare new session: create detail objects for the new session.
#         min_lon = serializer.validated_data["min_lon"]
#         min_lat = serializer.validated_data["min_lat"]
#         max_lon = serializer.validated_data["max_lon"]
#         max_lat = serializer.validated_data["max_lat"]
#         edges, nodes, users, activities, min_lon, min_lat, max_lon, max_lat, origin_creator = \
#             SessionViewSet.prepare_new()
#         # Save session and its details within a database transaction.
#         try:
#             with transaction.atomic():
#                 session = serializer.save(active=True)
#                 # Save graph edges
#                 for edge in edges:
#                     edge.session = session
#                     edge.save()
#                 # Save nodes.
#                 for node in nodes:
#                     node.session = session
#                     node.save()
#                 # # Save users.
#                 # users.append(models.SessionUser(origin=origin_creator, user=session.creator))
#                 # for user in users:
#                 #     user.session = session
#                 #     user.save()
#                 # # Save activities.
#                 # for activity in activities:
#                 #     activity.session = session
#                 #     activity.save()
#         except DatabaseError:
#             raise exceptions.NewSessionTransactionException

from django.shortcuts import render


def index(request):
    return render(request, 'csdp/index.html', {})
