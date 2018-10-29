from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.db import transaction
from django.db.utils import DatabaseError

import rs.models as models
import suitability
import vst_rs
from link_performance import identity
from rs.exceptions import SessionPlansTransactionException


def build_graph_from_model(session_id):
    graph = suitability.SuitabilityDigraph(capacitated=True)
    generator = suitability.SuitableNodeWeightGenerator()
    default_node_weight = generator.weights["FORGET_IT"]
    hotspot_weight = generator.weights["VERY_SUITABLE"]
    # Retrieve edges from the DB for this session.
    # Append edge by edge to the new graph.
    # Nodes' weights are initialized.
    session_edges = models.SessionGraphEdge.objects.filter(session__id=session_id)
    for session_edge in session_edges:
        edge = (session_edge.node_i, session_edge.node_j)
        graph.append_edge_2(edge,
                            session_edge.weight,
                            nodes_weights=(default_node_weight, default_node_weight),
                            capacity=1.0,
                            check_exists=False)
    # Hot-spots' weights have to be updated.
    # Therefore, hot-spots are retrieved from DB for this session.
    hotspots = models.SessionGraphNode.objects.filter(session__id=session_id, node_type="H")
    node_weights = {hotspot.node: hotspot_weight for hotspot in hotspots}
    graph.update_node_weights(node_weights)
    return graph


def build_queries_from_model(session_id):
    # Retrieve users and POIs for this session.
    session_users = models.SessionUser.objects.filter(session__id=session_id)
    pois = models.SessionGraphNode.objects.filter(session__id=session_id)
    # Create dictionaries of users and POIs per activity.
    users_per_activity = dict()
    for session_user in session_users:
        users_per_activity.setdefault(session_user.activity, []).append(session_user.origin)
    pois_per_activity = dict()
    for poi in pois:
        pois_per_activity.setdefault(poi.activity, []).append(poi.node)
    # Merge both dictionaries into the queries
    queries = [(users, pois_per_activity[activity], activity) for activity, users in users_per_activity.iteritems()]
    return queries


# def prepare_plan_details(plan):
#     details = []
#     for edge in plan.get_edges():
#         detail = models.SessionPlanDetail()


@shared_task
def compute_plan(session):
    # Build graph and queries for this session.
    graph = build_graph_from_model(session.id)
    queries = build_queries_from_model(session.id)
    # Compute plan
    queries_ = [(users, pois) for users, pois, _ in queries]
    vstrs = vst_rs.VST_RS(graph)
    plans, c, _, _, _, _, _ = vstrs.non_congestion_aware(queries_, 4, 8, identity, merge_users=False, verbose=True)
    # Save plan and its details within a database transaction.
    try:
        with transaction.atomic():
            session.travel_cost = c
            session.save()
            for ord_, plan in plans:
                # Save session plan (plan for one activity)
                # TODO: Include travel cost per plan (per activity)
                session_plan = models.SessionPlan(session=session, activity=queries[ord_][2])
                session_plan.save()
                # Save edges of this plan.
                edges = plan.get_edges()
                for edge in edges:
                    session_plan_edge = models.SessionPlanDetail(plan=session_plan, node_i=edge[0], node_j=edge[1])
                    session_plan_edge.save()
    except DatabaseError:
        raise SessionPlansTransactionException
    return True

