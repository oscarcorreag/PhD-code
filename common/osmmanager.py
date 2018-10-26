import numpy as np

from osmdbmanager import OsmDBManager
from suitability import SuitabilityDigraph
from utils import haversine


def generate_graph(results, generator, cost_type="distance", capacitated=False):
    graph = SuitabilityDigraph(capacitated=capacitated)
    #
    prev_way_id = None
    prev_node_id = None
    hotspots = set()
    pois = set()
    for r in results:
        way_id = r[0]
        node_id = r[1]
        type_ = r[3]
        stype = r[4]
        lat = float(r[5])
        lon = float(r[6])
        sa1_code = r[7]
        sa2_code = r[8]
        hw_type = r[9]
        if node_id not in graph:
            if type_ == "hotspot":
                graph[node_id] = (generator.weights["VERY_SUITABLE"][0], {}, {'lat': lat, 'lon': lon, 'sa1': sa1_code,
                                                                              'sa2': sa2_code, 'subtype': stype})
                hotspots.add(node_id)
            else:
                if type_ == "poi":
                    pois.add(node_id)
                graph[node_id] = (generator.weights["WARNING"][0], {}, {'lat': lat, 'lon': lon, 'sa1': sa1_code,
                                                                        'sa2': sa2_code, 'subtype': stype})
        if prev_way_id == way_id:
            prev_lat = graph[prev_node_id][2]['lat']
            prev_lon = graph[prev_node_id][2]['lon']
            # Cost estimation
            cost = 0
            distance = haversine(lat, lon, prev_lat, prev_lon)
            if cost_type == "distance":
                cost = distance
            elif cost_type == "travel_time":
                cost = osm_avg(distance, hw_type)
            #
            graph[node_id][1][prev_node_id] = cost
            graph[prev_node_id][1][node_id] = cost
        prev_way_id = way_id
        prev_node_id = node_id
    #
    # pdb.set_trace()
    isolated = []
    # Both dictionaries will INCLUDE HOT SPOTS AND POIs.
    nodes_by_sa1_code = {}
    nodes_by_sa2_code = {}
    #
    for node_id, info in graph.iteritems():
        if len(info[1]) == 0 or (len(info[1]) == 1 and info[1].keys()[0] == node_id):
            isolated.append(node_id)
        else:
            sa1_code = info[2]['sa1']
            sa2_code = info[2]['sa2']
            if sa1_code in nodes_by_sa1_code:
                nodes_by_sa1_code[sa1_code].append(node_id)
            else:
                nodes_by_sa1_code[sa1_code] = [node_id]
            if sa2_code in nodes_by_sa2_code:
                nodes_by_sa2_code[sa2_code].append(node_id)
            else:
                nodes_by_sa2_code[sa2_code] = [node_id]
    for node_id in isolated:
        del graph[node_id]
        if node_id in hotspots:
            hotspots.remove(node_id)
        if node_id in pois:
            pois.remove(node_id)
    #
    print "h:", len(hotspots), "p:", len(pois)

    return graph, list(hotspots), list(pois), nodes_by_sa1_code, nodes_by_sa2_code


'''
MAX_SPEEDS come from the following query to OSM database:

            SELECT	speeds.hw_type,
                ceil(avg(speeds.max_speed))
            FROM
                (
                    SELECT	(
                            SELECT	way_tags.value
                            FROM	way_tags
                            WHERE	way_tags.way_id = ways.way_id
                            AND	key = 'highway'
                        ) hw_type,
                        (
                            SELECT	cast(way_tags.value as integer)
                            FROM	way_tags
                            WHERE	way_tags.way_id = ways.way_id
                            AND	key = 'maxspeed'
                            AND value != 'none'
                        ) max_speed
                    FROM	ways
                ) speeds
            WHERE	speeds.max_speed IS NOT NULL
            GROUP BY
                speeds.hw_type
'''
MAX_SPEEDS = {
    "construction": 49,
    "cycleway": 34,
    "footway": 36,
    "living_street": 16,
    "motorway": 98,
    "motorway_link": 88,
    "path": 21,
    "pedestrian": 28,
    "primary": 68,
    "primary_link": 66,
    "proposed": 55,
    "residential": 50,
    "road": 100,
    "secondary": 70,
    "secondary_link": 65,
    "service": 40,
    "tertiary": 59,
    "tertiary_link": 57,
    "track": 72,
    "trunk": 75,
    "trunk_link": 66,
    "unclassified": 61,
    "steps": 1,
    "bus_guideway": 1,
    "raceway": 1,
    "": 88
}


def osm_avg(distance, hw_type):
    hw_type_ = ""
    if hw_type is not None:
        hw_type_ = hw_type
    return distance / (1000. * MAX_SPEEDS[hw_type_] * .5)


class OsmManager:
    def __init__(self):
        self.__osmdbmngr = OsmDBManager("postgres", "naya0105", "osm", "localhost")

    def get_nodes_for_bbox(self, min_lon, min_lat, max_lon, max_lat, hotspots=True, pois=True):
        nodes = dict()
        results = self.__osmdbmngr.get_graph_nodes_for_bbox(min_lon, min_lat, max_lon, max_lat, hotspots, pois)
        for r in results:
            node_id = r[1]
            type_ = r[3]
            stype = r[4]
            lat = float(r[5])
            lon = float(r[6])
            sa1_code = r[7]
            sa2_code = r[8]
            nodes[node_id] = {'type': type_, 'lat': lat, 'lon': lon, 'sa1': sa1_code, 'sa2': sa2_code, 'subtype': stype}
        return nodes

    def generate_graph_for_file(self, file_, act, generator, hotspots=True, pois=True, cost_type="distance"):
        results = self.__osmdbmngr.get_graph_nodes_for_file(file_, act, hotspots, pois)
        return generate_graph(results, generator, cost_type=cost_type)

    def generate_graph_for_bbox(self, min_lon, min_lat, max_lon, max_lat, generator, hotspots=True, pois=True,
                                cost_type="distance"):
        results = self.__osmdbmngr.get_graph_nodes_for_bbox(min_lon, min_lat, max_lon, max_lat, hotspots, pois)
        return generate_graph(results, generator, cost_type=cost_type)

    def choose_terminals_according_to_vista(self, file_, dh, act, nodes_by_sa1_code, excluded_nodes=None):
        #
        if excluded_nodes is None:
            excluded_nodes = []
        #
        people = self.__osmdbmngr.get_people(file_, dh, act)
        people_by_sa1_code = {}
        for orig_sa1_code, _ in people:
            if orig_sa1_code in people_by_sa1_code:
                people_by_sa1_code[orig_sa1_code] += 1
            else:
                people_by_sa1_code[orig_sa1_code] = 1
        #
        terminals = set()
        for orig_sa1_code, c in people_by_sa1_code.iteritems():
            nodes = list(set(nodes_by_sa1_code[orig_sa1_code]).difference(excluded_nodes))
            indices = np.random.choice(a=len(nodes), size=c)
            terminals.update([nodes[i] for i in indices])
        print "t:", len(terminals)
        return list(terminals)

    def choose_hotspots_according_to_population(self, sa3_code11, nh, nodes_by_sa2_code, excluded_nodes=None):
        #
        if excluded_nodes is None:
            excluded_nodes = []
        #
        sa2_codes = self.__osmdbmngr.get_sa2_codes(sa3_code11)
        pop_stats = self.get_population_stats(sa3_code11)
        tot_pop = sum(pop_stats.values())
        #
        hotspots = []
        for i, sa2_5dig11_l in enumerate(sa2_codes):
            sa2_5dig11 = int(sa2_5dig11_l[0])
            nh_sa2 = int(round(nh * float(pop_stats[sa2_5dig11]) / tot_pop, 0))
            if i == len(sa2_codes) - 1:
                nh_sa2 = nh - len(hotspots)
            # print nh_sa2
            nodes = list(set(nodes_by_sa2_code[sa2_5dig11_l[0]]).difference(excluded_nodes))
            indices = np.random.choice(a=len(nodes), size=nh_sa2, replace=False)
            hotspots.extend([nodes[i] for i in indices])
        return hotspots

    def get_departure_hours(self, file_):
        return self.__osmdbmngr.get_departure_hours(file_)

    def get_dest_activities(self, file_, dh):
        return self.__osmdbmngr.get_dest_activities(file_, dh)

    def get_sa1_codes_by_sa2(self, sa3_code11):
        #
        sa1_codes = self.__osmdbmngr.get_sa1_codes(sa3_code11)
        #
        sa2_codes = {}
        for sa2_5dig11_s, sa1_7dig11 in sa1_codes:
            sa2_5dig11 = int(sa2_5dig11_s)
            if sa2_5dig11 in sa2_codes:
                sa2_codes[sa2_5dig11].append(sa1_7dig11)
            else:
                sa2_codes[sa2_5dig11] = [sa1_7dig11]
        return sa2_codes

    def get_population_stats(self, sa3_code11):
        pop_stats = self.__osmdbmngr.get_population_stats(sa3_code11)
        return {sa2_5dig11: est_pop for sa2_5dig11, est_pop in pop_stats}

    def generate_samples(self, sa3_code11, sample_table):
        stats = self.__osmdbmngr.get_statistics(sa3_code11)
        sa2_codes = self.get_sa1_codes_by_sa2(sa3_code11)
        pop_stats = self.get_population_stats(sa3_code11)
        tot_pop = sum(pop_stats.values())
        #
        samples = []
        for dh, td, mt, da, nt in stats:
            for sa2_5dig11, sa1_codes in sa2_codes.iteritems():
                nt_sa2 = int(nt * float(pop_stats[sa2_5dig11]) / tot_pop)
                print nt_sa2
                for _ in range(nt_sa2):
                    ind = np.random.choice(a=len(sa1_codes), size=1)
                    sample = [sa1_codes[ind], da, dh, td, mt]
                    samples.append(sample)
        self.__osmdbmngr.save_samples(samples, sample_table)

    def get_knn(self, lon, lat, k, min_dist=None):
        return self.__osmdbmngr.get_knn(lon, lat, k, min_dist)

    def get_coordinates(self, node):
        return self.__osmdbmngr.get_coordinates(node)

    def get_session_users(self, session_id):
        return self.__osmdbmngr.get_session_users(session_id)

    def get_session_user_by_pk(self, pk):
        return self.__osmdbmngr.get_session_user_by_pk(pk)

    def get_session_user(self, session_id, user_id):
        return self.__osmdbmngr.get_session_user(session_id, user_id)

