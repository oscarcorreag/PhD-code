import json
import numpy as np
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from suitability import SuitabilityDigraph
from vst_rs import VST_RS
from link_performance import bpr, bpr_log


def get_suitability_graph_from_session(request):
    graph = request.session['graph']
    suitability_graph = SuitabilityDigraph()
    for node_id, (node_weight, adj_dict, data) in graph.items():
        new_adj_dict = {int(neighbour): edge_cost for neighbour, edge_cost in adj_dict.items()}
        suitability_graph[int(node_id)] = (node_weight, new_adj_dict, data)
    return suitability_graph


def get_queries_from_session(request):
    qs = request.session['queries']
    queries = []
    for ts, pois, subtype in qs:
        queries.append(([int(t) for t in ts], pois, subtype))
    return queries


def get_geo_forest_edges(subtype, plan, geo_suit_graph):
    edges = plan.get_edges()
    geo_forest_edges = []
    for e in edges:
        from_ = (geo_suit_graph[e[0]][2]['lat'], geo_suit_graph[e[0]][2]['lon'])
        to_ = (geo_suit_graph[e[1]][2]['lat'], geo_suit_graph[e[1]][2]['lon'])
        geo_forest_edges.append((from_, to_, subtype))
    return geo_forest_edges


def index(request):
    generator = SuitableNodeWeightGenerator()

    # Long integers seem not to be JSON serializable. Thus, str() function is used whenever the integer does not come
    # from session or from the DB. (Not pretty sure!)

    if 'op' in request.GET:
        #
        top = request.GET.get('top')
        left = request.GET.get('left')
        bottom = request.GET.get('bottom')
        right = request.GET.get('right')
        print top, left, bottom, right
        #
        min_lon = min(left, right)
        min_lat = min(top, bottom)
        max_lon = max(left, right)
        max_lat = max(top, bottom)
        #
        osm = OsmManager()

        # CREATE NETWORK SAMPLE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if request.GET['op'] == 'show_pois':
            graph, _, pois, _, _ = \
                osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator, hotspots=False,
                                            cost_type="travel_time")
            #
            request.session['graph'] = graph
            # request.session['graph'] = {(str(e[0]), str(e[1])): v for e, v in graph.edges.items()}
            request.session['pois'] = pois
            #
            geo_pois = [(graph[p][2]['lat'], graph[p][2]['lon'], p, graph[p][2]['subtype']) for p in pois]

            return HttpResponse(json.dumps(
                dict(
                    isOk=1,
                    content=render_to_string('congestion/index.html', {}),
                    pois=geo_pois,
                )
            ))  # , default=decimal_default))

        # SLICE POIS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif request.GET['op'] == 'slice_pois':
            graph = get_suitability_graph_from_session(request)
            pois = request.session['pois']
            #
            s_pois = osm.get_nodes_for_bbox(min_lon, min_lat, max_lon, max_lat, hotspots=False)
            s_pois = set(pois).intersection(s_pois)
            #
            request.session['pois'] = list(s_pois)
            #
            geo_pois = [(graph[p][2]['lat'], graph[p][2]['lon'], p, graph[p][2]['subtype']) for p in s_pois]

            return HttpResponse(json.dumps(
                dict(
                    isOk=1,
                    content=render_to_string('congestion/index.html', {}),
                    pois=geo_pois,
                )
            ))  # , default=decimal_default))

        # CREATE QUERIES +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif request.GET['op'] == "create_queries":
            nuq = int(request.GET.get('nusers'))
            seed = request.GET.get('seed')
            #
            graph = get_suitability_graph_from_session(request)
            pois = request.session['pois']
            # How many different activities were sliced?
            ps_subtype = dict()
            for p in pois:
                ps_subtype.setdefault(graph[p][2]['subtype'], []).append(p)
            #
            s_nodes = osm.get_nodes_for_bbox(min_lon, min_lat, max_lon, max_lat, hotspots=False)
            s_nodes = set(graph.keys()).intersection(s_nodes).difference(pois)
            #
            queries = []
            ts_subtype = dict()
            occupied = set()
            np.random.seed(int(seed))
            for subtype, pois_ in ps_subtype.items():
                where = set(s_nodes).difference(occupied)
                terminals = np.random.choice(a=list(where), size=nuq, replace=False)
                queries.append(([str(t) for t in terminals], pois_, subtype))
                occupied.update(terminals)
                ts_subtype[subtype] = list(terminals)
            #
            request.session['queries'] = queries
            #
            geo_pois = [(graph[p][2]['lat'], graph[p][2]['lon'], p, graph[p][2]['subtype']) for p in pois]
            geo_terminals = []
            for subtype, ts in ts_subtype.items():
                for t in ts:
                    geo_terminals.append((graph[t][2]['lat'], graph[t][2]['lon'], str(t), subtype))

            return HttpResponse(json.dumps(
                dict(
                    isOk=1,
                    content=render_to_string('congestion/index.html', {}),
                    pois=geo_pois,
                    terminals=geo_terminals,
                )
            ))  # , default=decimal_default))

    elif 'alg' in request.GET:
        alg = request.GET.get('alg')
        print alg
        # Set up the graph.
        graph = get_suitability_graph_from_session(request)
        graph.capacitated = True
        graph.set_capacities({e: 2 for e in graph.get_edges()})  # FIX THIS +++++++++++++++++++++++++++++++++++++++++++
        #
        queries = get_queries_from_session(request)
        queries_ = [(ts, pois) for ts, pois, _ in queries]
        #
        ni = 0
        #
        # with open('file_tt.txt', 'w') as file_:
        #     file_.write(json.dumps(graph))
        #
        merge_users = False
        max_iter = 20
        alpha = 1.0
        beta = 4.0
        vst_rs = VST_RS(graph)

        st = time.clock()
        if alg == 'vst-nca':
            plans, cost, warl, mwrl, mrl1, mrl2, entropy = \
                vst_rs.non_congestion_aware(queries_, 4, 8, bpr, merge_users=merge_users, alpha=alpha, beta=beta,
                                            verbose=True)
        elif alg == "vst-ca-mixed":
            plans, cost, warl, mwrl, mrl1, mrl2, entropy, ni = \
                vst_rs.congestion_aware(queries_, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter, alpha=alpha,
                                        beta=beta, verbose=True, randomize=True)
        else:
            plans, cost, warl, mwrl, mrl1, mrl2, entropy, ni = \
                vst_rs.congestion_aware(queries_, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter, alpha=alpha,
                                        beta=beta, verbose=True, randomize=False)
        elapsed_time = time.clock() - st
        #
        geo_edges = []
        for ord_, plan in plans:
            geo_edges.extend(get_geo_forest_edges(queries[ord_][2], plan, graph))

        return HttpResponse(json.dumps(dict(
            content=render_to_string('congestion/index.html', {}),
            route=geo_edges,
            cost=cost,
            elapsed_time=elapsed_time,
            warl=warl,
            mwrl=mwrl,
            mrl1=mrl1,
            mrl2=mrl2,
            ent=entropy,
            ni=ni
        )))

    else:
        return render(request, 'congestion/index.html', {})
