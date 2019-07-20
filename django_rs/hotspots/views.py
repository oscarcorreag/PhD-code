import json
import sys
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from hotspot_based import HotspotBased
from osmmanager import OsmManager
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from vst_rs import VST_RS


def get_suitability_graph_from_session(request):
    graph = request.session['graph']
    suitability_graph = SuitabilityGraph()
    for node_id, (node_weight, adj_dict, data) in graph.iteritems():
        new_adj_dict = {int(neighbour): edge_cost for neighbour, edge_cost in adj_dict.iteritems()}
        suitability_graph[int(node_id)] = (node_weight, new_adj_dict, data)
    dist = {}
    for k, v in request.session['dist'].iteritems():
        k_ = k.split(",")
        dist[(long(k_[0]), long(k_[1]))] = v
    suitability_graph.dist = dist
    pairs = set()
    for k in request.session['pairs_dist_paths']:
        k_ = k.split(",")
        pairs.add((long(k_[0]), long(k_[1])))
    suitability_graph.pairs_dist_paths = pairs

    return suitability_graph


def get_geo_steiner_tree_edges(steiner_tree, geo_suit_graph):
    edges = steiner_tree.get_edges()
    geo_steiner_tree_edges = []
    for e in edges:
        from_ = (geo_suit_graph[e[0]][2]['lat'], geo_suit_graph[e[0]][2]['lon'])
        to_ = (geo_suit_graph[e[1]][2]['lat'], geo_suit_graph[e[1]][2]['lon'])
        geo_steiner_tree_edges.append((from_, to_))
    return geo_steiner_tree_edges


def index(request):
    #
    generator = SuitableNodeWeightGenerator()
    if 'file_to_retrieve_dhs' in request.GET:
        #
        file_ = request.GET.get('file_to_retrieve_dhs')
        osm = OsmManager()
        dep_hours = osm.get_departure_hours(file_)
        return HttpResponse(json.dumps(dict(dh=dep_hours)))

    elif 'file_to_retrieve_acts' in request.GET and 'dh_to_retrieve_acts' in request.GET:
        #
        file_ = request.GET.get('file_to_retrieve_acts')
        dh = request.GET.get('dh_to_retrieve_acts')
        osm = OsmManager()
        dest_acts = osm.get_dest_activities(file_, dh)
        return HttpResponse(json.dumps(dict(acts=dest_acts)))

    elif 'file' in request.GET and 'dh' in request.GET and 'act' in request.GET:
        #
        file_ = request.GET.get('file')
        dh = request.GET.get('dh')
        act = request.GET.get('act')
        print file_, dh, act
        #
        osm = OsmManager()
        graph, hotspots, pois, nodes_by_sa1_code, nodes_by_sa2_code = osm.generate_graph_for_file(file_, act, generator)
        terminals = osm.choose_terminals_according_to_vista(file_, dh, act, nodes_by_sa1_code)

        reset_hotspots_weights = {h: generator.weights["WARNING"][0] for h in hotspots}
        graph.update_node_weights(reset_hotspots_weights)

        excluded = list(pois)
        excluded.extend(terminals)
        # rest_nodes = list(set(graph.keys()).difference(excluded))

        # # Option A: Hot-spots are the rest of the nodes, i.e., users can meet anywhere.
        # hotspots = list(rest_nodes)

        # # Option B: Hot-spots chosen randomly from the rest of the nodes, i.e., nodes that aren't terminals nor POIs.
        # ind = np.random.choice(a=len(rest_nodes), size=len(hotspots), replace=False)
        # hotspots = [rest_nodes[i] for i in ind]

        # Option C: Hot-spots chosen based on population distribution.
        # TODO: Dynamic sa3 code
        hotspots = osm.choose_hotspots_according_to_population(21303, len(hotspots), nodes_by_sa2_code, excluded)

        weights = {h: generator.weights["VERY_SUITABLE"][0] for h in hotspots}
        graph.update_node_weights(weights)

        temp = list(hotspots)
        temp.extend(pois)
        temp.extend(terminals)
        graph.compute_dist_paths(origins=temp, destinations=temp, compute_paths=False)
        #
        request.session['graph'] = graph
        request.session['dist'] = {str(k[0]) + "," + str(k[1]): v for k, v in graph.dist.iteritems()}
        request.session['pairs_dist_paths'] = [str(v) + "," + str(w) for v, w in graph.pairs_dist_paths]
        request.session['hotspots'] = hotspots
        request.session['pois'] = pois
        request.session['terminals'] = terminals
        #
        geo_hotspots = [(graph[h][2]['lat'], graph[h][2]['lon'], h) for h in hotspots]
        geo_pois = [(graph[p][2]['lat'], graph[p][2]['lon'], p) for p in pois]
        geo_terminals = [(graph[t][2]['lat'], graph[t][2]['lon'], t) for t in terminals]

        return HttpResponse(json.dumps(dict(
            isOk=1,
            content=render_to_string('hotspots/index.html', {}),
            hotspots=geo_hotspots,
            pois=geo_pois,
            terminals=geo_terminals,
        )))  # , default=decimal_default))

    elif 'alg' in request.GET:
        alg = request.GET.get('alg')
        print alg
        #
        graph = get_suitability_graph_from_session(request)
        hotspots = request.session['hotspots']
        pois = request.session['pois']
        terminals = request.session['terminals']
        # pdb.set_trace()
        #
        if alg == 'rahman':
            cap = int(request.GET.get('cap_r'))
            vst_rs = VST_RS(graph, nodes=hotspots)
            start_time = time.clock()
            forest, cost, gr, avg_dr, num_trees, avg_or, _, _ = vst_rs.steiner_forest(terminals, pois, cap, 8)
            elapsed_time = time.clock() - start_time
        else:
            cap = int(request.GET.get('cap_c'))
            mdr = request.GET.get('mdr')
            mwd = request.GET.get('mwd')
            if mdr is not None and mdr != '':
                mdr = float(request.GET.get('mdr'))
            else:
                mdr = sys.maxint
            if mwd is not None and mwd != '':
                mwd = float(request.GET.get('mwd'))
            else:
                mwd = sys.maxint
            # print mdr, mwd
            hb = HotspotBased(graph, terminals, pois)
            start_time = time.clock()
            forest, cost, gr, avg_dr, num_trees, avg_or, _ = \
                hb.steiner_forest(k=cap, max_dr=mdr, max_wd=mwd, get_lsv=False)
            elapsed_time = time.clock() - start_time
        #
        geo_steiner_tree_edges = get_geo_steiner_tree_edges(forest, graph)

        return HttpResponse(json.dumps(dict(
            content=render_to_string('hotspots/index.html', {}),
            route=geo_steiner_tree_edges,
            distance=cost,
            elapsed_time=elapsed_time,
            gr=gr,
            avg_dr=avg_dr,
            num_cars=num_trees,
            avg_or=avg_or
        )))

    else:
        return render(request, 'hotspots/index.html', {})
