import pg8000
import time
import pdb


def get_travel_period_code(travel_period):
    if travel_period == "Weekday":
        return 0
    return 1


def get_travel_method_code(travel_method):
    if travel_method == "Walking":
        return 0
    if travel_method == "Bicycle":
        return 1
    return 2


FIELDS_SESSION_USER = ["rs_sessionuser.id",
                       "rs_sessionuser.user_id",
                       "session_id",
                       "join_time",
                       "origin",
                       "destination",
                       "activity",
                       "ready_to_travel",
                       "longitude",
                       "latitude"]


def map_record_session_user(record):
    map_ = {field: record[i] for i, field in enumerate(FIELDS_SESSION_USER) if not field.startswith("rs_sessionuser.")}
    map_["id"] = record[0]
    map_["user_id"] = record[1]
    return map_


class OsmDBManager:
    def __init__(self, user, password, database, host):
        self.__conn = pg8000.connect(user=user, password=password, database=database, host=host)
        self.__cursor = self.__conn.cursor()

    def get_inc_nodes_by_type(self, target_table, key_, value_):

        statement = "SELECT DISTINCT way_nodes.node_id " \
                    "FROM   way_nodes " \
                    "INNER JOIN" \
                    "       ( " \
                    "           SELECT  node_id " \
                    "           FROM    way_nodes " \
                    "           INNER JOIN way_tags " \
                    "           ON      way_nodes.way_id = way_tags.way_id " \
                    "           WHERE   way_tags.key = %s " \
                    "           AND     way_tags.value = %s " \
                    "           AND     way_nodes.way_id IN " \
                    "                   ( " \
                    "                       SELECT  way_id " \
                    "                       FROM    way_nodes " \
                    "                       WHERE   node_id IN " \
                    "                               ( " \
                    "                                   SELECT  node_id " \
                    "                                   FROM    way_nodes " \
                    "                                   INNER JOIN way_tags " \
                    "                                   ON      way_nodes.way_id = way_tags.way_id " \
                    "                                   AND     way_tags.key = 'highway' " \
                    "                                   AND     way_tags.value IN " \
                    "                                           ( " \
                    "                                               'motorway', " \
                    "                                               'trunk', " \
                    "                                               'primary', " \
                    "                                               'secondary', " \
                    "                                               'tertiary', " \
                    "                                               'service', " \
                    "                                               'residential', " \
                    "                                               'living_street', " \
                    "                                               'motorway_link', " \
                    "                                               'trunk_link', " \
                    "                                               'primary_link', " \
                    "                                               'secondary_link', " \
                    "                                               'tertiary_link', " \
                    "                                               'unclassified' " \
                    "                                           ) " \
                    "                                   GROUP BY node_id " \
                    "                                   HAVING  COUNT(*) >= 2 " \
                    "                               ) " \
                    "                   ) " \
                    "           UNION " \
                    "           SELECT  node_id " \
                    "           FROM    node_tags " \
                    "           WHERE   node_tags.key = %s " \
                    "           AND     node_tags.value = %s " \
                    "       ) special_nodes " \
                    "ON     way_nodes.node_id = special_nodes.node_id " \
                    "AND    way_nodes.node_id NOT IN (SELECT node_id FROM " + target_table + ")"

        self.__cursor.execute(statement, (key_, value_, key_, value_))
        return self.__cursor.fetchall()

    def save_hotspots(self, hotspots):
        for h in hotspots:
            self.__cursor.execute("INSERT INTO hotspots (node_id, hotspot_type) VALUES (%s, %s)", (h[0], h[1]))

    def copy_hotspots_by_type(self, key_, value_):
        # BEFORE HAVE A LOOK AT C:\Users\oscarcg\Dropbox\Education\Unimelb PhD\datasets\OSM utils\Get hotspots.sql
        hotspots = self.get_inc_nodes_by_type("hotspots", key_, value_)
        hotspots_w_type = [[h[0], key_ + ":" + value_] for h in hotspots]
        self.save_hotspots(hotspots_w_type)
        self.__conn.commit()

    def save_pois(self, pois):
        for p in pois:
            self.__cursor.execute("INSERT INTO pois (actual_node_id, node_id, poi_type) VALUES (%s, %s, %s)",
                                  (p[0], p[0], p[1]))

    def copy_pois_by_type(self, key_, value_):

        pois = self.get_inc_nodes_by_type("pois", key_, value_)
        pois_w_type = [[p[0], key_ + ":" + value_] for p in pois]
        self.save_pois(pois_w_type)
        self.__conn.commit()

    '''
    Get nodes that belong to different types of [highway].
    '''
    def get_highway_nodes(self):

        statement = "SELECT node_id " \
                    "FROM   way_nodes " \
                    "INNER JOIN way_tags " \
                    "ON     way_nodes.way_id = way_tags.way_id " \
                    "AND    way_tags.key = 'highway' " \
                    "AND    way_tags.value IN " \
                    "       ( " \
                    "           'motorway', " \
                    "           'trunk', " \
                    "           'primary', " \
                    "           'secondary', " \
                    "           'tertiary', " \
                    "           'service', " \
                    "           'residential', " \
                    "           'living_street', " \
                    "           'motorway_link', " \
                    "           'trunk_link', " \
                    "           'primary_link', " \
                    "           'secondary_link', " \
                    "           'tertiary_link', " \
                    "           'unclassified' " \
                    "       ) " \
                    "AND    way_nodes.node_id NOT IN (SELECT node_id FROM highway_nodes) " \
                    "GROUP BY node_id " \
                    "HAVING  COUNT(*) >= 2"

        self.__cursor.execute(statement)
        return self.__cursor.fetchall()

    def save_highway_nodes(self, highway_nodes):
        for h in highway_nodes:
            self.__cursor.execute("INSERT INTO highway_nodes (node_id) VALUES (%s)", (h))

    def copy_highway_nodes(self):
        highway_nodes = self.get_highway_nodes()
        self.save_highway_nodes(highway_nodes)
        self.__conn.commit()

    def get_departure_hours(self, file_):
        statement = 'SELECT DISTINCT "DEPHOUR" ' \
                    'FROM   "' + file_ + '" ' \
                    'WHERE  "TRAVELPERIOD" = 0 ' \
                    'AND    "TRAVELMETHOD" = 2 ' \
                    'ORDER BY ' \
                    '       "DEPHOUR"'
        self.__cursor.execute(statement)
        results = self.__cursor.fetchall()
        return [r[0] for r in results]

    def get_dest_activities(self, file_, dh):
        statement = 'SELECT DISTINCT "DESTPLACE2", ' \
                    '       "desc" ' \
                    'FROM   "' + file_ + '" ' \
                    'INNER JOIN ' \
                    '       "VistaPoiTypes" ' \
                    'ON     "' + file_ + '"."DESTPLACE2" = "VistaPoiTypes".code ' \
                    'WHERE  "DEPHOUR" = ' + str(dh) + ' ' \
                    'AND    "TRAVELPERIOD" = 0 ' \
                    'AND    "TRAVELMETHOD" = 2 ' \
                    'ORDER BY ' \
                    '       "desc"'
        self.__cursor.execute(statement)
        results = self.__cursor.fetchall()
        return [(r[0], r[1]) for r in results]

    def get_mapped_osm_act(self, act):
        statement = "SELECT DISTINCT osm_poi_type FROM mapping_vista_osm_poi_types WHERE vista_code = " + str(act)
        self.__cursor.execute(statement)
        results = self.__cursor.fetchall()
        return [r[0] for r in results]

    def get_people(self, file_, dh, act):
        # Only TRAVELPERIOD = "Weekday" and TRAVELMETHOD = "Vehicle Driver"
        statement = 'SELECT DISTINCT "ORIG_SA1", ' \
                    '       "PERSID" ' \
                    'FROM   "' + file_ + '" ' \
                    'WHERE  "DEPHOUR" = %s ' \
                    'AND    "DESTPLACE2" = %s ' \
                    'AND    "TRAVELPERIOD" = 0 ' \
                    'AND    "TRAVELMETHOD" = 2'
        self.__cursor.execute(statement, (dh, act))
        results = self.__cursor.fetchall()
        return [(r[0], r[1]) for r in results]

    def get_sa1_codes(self, sa3_code11):
        statement = "SELECT sa2_5dig11, sa1_7dig11 FROM sa1_2011_aust WHERE sa3_code11 = '" + str(sa3_code11) + "'"
        self.__cursor.execute(statement)
        return self.__cursor.fetchall()

    def get_sa2_codes(self, sa3_code11):
        statement = "SELECT DISTINCT sa2_5dig11 FROM sa1_2011_aust WHERE sa3_code11 = '" + str(sa3_code11) + "'"
        self.__cursor.execute(statement)
        return self.__cursor.fetchall()

    def get_sa3_codes(self, file_):
        statement = 'SELECT DISTINCT sa3_code11 ' \
                    'FROM   "' + file_ + '" ' \
                    'INNER JOIN ' \
                    '       sa1_2011_aust ' \
                    'ON     "' + file_ + '"."ORIG_SA1" = sa1_2011_aust.sa1_7dig11'
        self.__cursor.execute(statement)
        results = self.__cursor.fetchall()
        return [r[0] for r in results]

    def get_graph_nodes_for_file(self, file_, act, get_hotspots, get_pois):

        sa3_codes = self.get_sa3_codes(file_)
        sa3_codes_s = "("
        for sa3_code in sa3_codes:
            sa3_codes_s += "'" + sa3_code + "',"
        sa3_codes_s = sa3_codes_s[:-1] + ")"
        # print sa3_codes_s
        hotspots_stmt = ""
        pois_stmt = ""
        if get_hotspots:
            hotspots_stmt = "UNION SELECT node_id, 'hotspot' p, '' t FROM hotspots"
        if get_pois:
            poi_types = self.get_mapped_osm_act(act)
            poi_types_s = "("
            for pt in poi_types:
                poi_types_s += "'" + pt + "',"
            poi_types_s = poi_types_s[:-1] + ")"
            pois_stmt = "UNION SELECT node_id, 'poi' p, poi_type t FROM pois WHERE   poi_type IN " + poi_types_s
            # print poi_types_s
        statement = "SELECT way_nodes.way_id, " \
                    "       way_nodes.node_id, " \
                    "       way_nodes.ord, " \
                    "       filtered_nodes.p, " \
                    "       filtered_nodes.t, " \
                    "       nodes.latitude, " \
                    "       nodes.longitude, " \
                    "       sa1_2011_aust.sa1_7dig11, " \
                    "       sa1_2011_aust.sa2_5dig11, " \
                    "       ( " \
                    "           SELECT  way_tags.value " \
                    "           FROM    way_tags " \
                    "           WHERE   way_tags.way_id = way_nodes.way_id " \
                    "           AND     key = 'highway' " \
                    "       ) hw_type " \
                    "FROM   way_nodes " \
                    "INNER JOIN " \
                    "       ( " \
                    "           SELECT  node_id, '' p, '' t " \
                    "           FROM    highway_nodes " + hotspots_stmt + " " + pois_stmt + " " \
                    "       ) filtered_nodes " \
                    "ON     way_nodes.node_id = filtered_nodes.node_id " \
                    "INNER JOIN " \
                    "       nodes " \
                    "ON		filtered_nodes.node_id = nodes.node_id " \
                    "INNER JOIN " \
                    "       sa1_2011_aust " \
                    "ON     ST_Intersects(nodes.geom, sa1_2011_aust.geom) " \
                    "WHERE	sa1_2011_aust.sa3_code11 IN " + sa3_codes_s + " " \
                    "ORDER BY " \
                    "       way_nodes.way_id, " \
                    "       way_nodes.ord"

        self.__cursor.execute(statement)
        return self.__cursor.fetchall()

    def get_graph_nodes_for_bbox(self, min_lon, min_lat, max_lon, max_lat, get_hotspots, get_pois):
        hotspots_stmt = ""
        pois_stmt = ""
        if get_hotspots:
            hotspots_stmt = "UNION SELECT node_id, 'hotspot' p, '' t FROM hotspots"
        if get_pois:
            pois_stmt = "UNION SELECT node_id, 'poi' p, poi_type t FROM pois"
        statement = "SELECT way_nodes.way_id, " \
                    "       way_nodes.node_id, " \
                    "       way_nodes.ord, " \
                    "       filtered_nodes.p, " \
                    "       filtered_nodes.t, " \
                    "       nodes.latitude, " \
                    "       nodes.longitude, " \
                    "       sa1_2011_aust.sa1_7dig11, " \
                    "       sa1_2011_aust.sa2_5dig11, " \
                    "       ( " \
                    "           SELECT  way_tags.value " \
                    "           FROM    way_tags " \
                    "           WHERE   way_tags.way_id = way_nodes.way_id " \
                    "           AND     key = 'highway' " \
                    "       ) hw_type " \
                    "FROM   way_nodes " \
                    "INNER JOIN " \
                    "       ( " \
                    "           SELECT  node_id, '' p, '' t " \
                    "           FROM    highway_nodes " + hotspots_stmt + " " + pois_stmt + " " \
                    "       ) filtered_nodes " \
                    "ON     way_nodes.node_id = filtered_nodes.node_id " \
                    "INNER JOIN " \
                    "       nodes " \
                    "ON		filtered_nodes.node_id = nodes.node_id " \
                    "LEFT JOIN " \
                    "       sa1_2011_aust " \
                    "ON     ST_Intersects(nodes.geom, sa1_2011_aust.geom) " \
                    "WHERE	nodes.geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326) " \
                    "ORDER BY " \
                    "       way_nodes.way_id, " \
                    "       way_nodes.ord"

        # pdb.set_trace()
        self.__cursor.execute(statement, (min_lon, min_lat, max_lon, max_lat))
        return self.__cursor.fetchall()

    def get_statistics(self, sa3_code11):
        statement = 'SELECT dephour, ' \
                    '       travel_day, ' \
                    '       method_travel, ' \
                    '       destplace, ' \
                    '       num_trips_trunc ' \
                    'FROM   "VistaStats" ' \
                    'WHERE  sa3_code11 = %s'
        self.__cursor.execute(statement, (sa3_code11))
        return self.__cursor.fetchall()

    def get_population_stats(self, sa3_code11):
        statement = 'SELECT sa2_5dig11, est_pop FROM "PopulationStats" WHERE sa3_code11 = ' + str(sa3_code11)
        self.__cursor.execute(statement)
        return self.__cursor.fetchall()

    def save_samples(self, samples, sample_table):
        for sample in samples:
            sa1_code = sample[0]
            da = sample[1]
            dh = sample[2]
            td = get_travel_period_code(sample[3])
            mt = get_travel_method_code(sample[4])
            statement = 'INSERT INTO ' + sample_table + ' ' \
                        '("ORIG_SA1", "DESTPLACE2", "DEPHOUR", "TRAVELPERIOD", "TRAVELMETHOD") ' \
                        'VALUES(%s, %s, %s, %s, %s)'
            self.__cursor.execute(statement, (str(sa1_code), da, dh, td, mt))
        self.__conn.commit()

    def save_experiment(self, experiment, save_details=True):
        stmt_1 = "INSERT INTO experiments (sa3_code11, dh, act, cost, gr, avg_dr, nt, avg_or, et, h, t, p, n, id, alg) " \
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        stmt_2 = "INSERT INTO experiment_details (id, alg, node_id, node_type) VALUES (%s, %s, %s, %s)"
        id_ = int(round(time.time() * 1000))
        for alg, (values, hs) in experiment.iteritems():
            values.extend([id_, alg])
            self.__cursor.execute(stmt_1, tuple(values))
            if not save_details:
                continue
            for h in hs:
                self.__cursor.execute(stmt_2, (id_, alg, h, 'hotspot'))
        self.__conn.commit()

    def get_knn(self, session_id, lon, lat, k, min_dist=None):

        where_stmt = ""

        if min_dist:
            where_stmt = "WHERE ST_Distance(geom, 'SRID=4326;POINT(" + str(lon) + " " + str(lat) + ")'::geometry) >= " \
                         + str(min_dist / 111111.)

        stmt = "SELECT  node_id, " \
               "        latitude, " \
               "        longitude, " \
               "        ST_Distance(geom, 'SRID=4326;POINT(" + str(lon) + " " + str(lat) + ")'::geometry) distance " \
               "FROM    graph_nodes_2 " \
               "INNER JOIN " \
               "        rs_sessiongraphnode " \
               "ON      graph_nodes_2.node_id = rs_sessiongraphnode.node " \
               "AND     rs_sessiongraphnode.session_id = %s " + where_stmt + " " \
               "ORDER BY " \
               "        geom <-> 'SRID=4326;POINT(" + str(lon) + " " + str(lat) + ")'::geometry limit " + str(k)

        self.__cursor.execute(stmt, (session_id,))
        queryset = self.__cursor.fetchall()

        return [{"node": node[0], "latitude": node[1], "longitude": node[2], "distance": node[3]} for node in queryset]

    def get_coordinates(self, node):
        stmt = "SELECT  longitude, " \
               "        latitude " \
               "FROM    nodes " \
               "WHERE   node_id = %s"
        self.__cursor.execute(stmt, (node,))
        record = self.__cursor.fetchone()
        if not record:
            return {}
        return {"longitude": record[0], "latitude": record[1]}

    def get_session_users(self, session_id):

        stmt = "SELECT  " + ', '.join(FIELDS_SESSION_USER) + " " \
               "FROM    rs_sessionuser " \
               "INNER JOIN " \
               "        nodes " \
               "ON      rs_sessionuser.origin = nodes.node_id " \
               "WHERE   session_id = %s"
        self.__cursor.execute(stmt, (session_id,))
        queryset = self.__cursor.fetchall()

        return [map_record_session_user(user) for user in queryset]

    def get_session_user_by_pk(self, pk):

        stmt = "SELECT  " + ', '.join(FIELDS_SESSION_USER) + " " \
               "FROM    rs_sessionuser " \
               "INNER JOIN " \
               "        nodes " \
               "ON      rs_sessionuser.origin = nodes.node_id " \
               "WHERE   id = %s"

        self.__cursor.execute(stmt, (pk,))
        queryset = self.__cursor.fetchall()

        result = {}
        if len(queryset) == 1:
            result = map_record_session_user(queryset[0])
        return result

    def get_session_user(self, session_id, user_id):

        stmt = "SELECT  " + ', '.join(FIELDS_SESSION_USER) + " " \
               "FROM    rs_sessionuser " \
               "INNER JOIN " \
               "        nodes " \
               "ON      rs_sessionuser.origin = nodes.node_id " \
               "WHERE   session_id = %s " \
               "AND     user_id = %s"

        self.__cursor.execute(stmt, (session_id, user_id))
        queryset = self.__cursor.fetchall()

        result = {}
        if len(queryset) == 1:
            result = map_record_session_user(queryset[0])
        return result

    def get_session_nodes(self, session_id, type_, activity=None):
        stmt = "SELECT  id, " \
               "        node, " \
               "        node_type, " \
               "        activity, " \
               "        longitude, " \
               "        latitude " \
               "FROM    rs_sessiongraphnode " \
               "INNER JOIN " \
               "        nodes " \
               "ON      rs_sessiongraphnode.node = nodes.node_id " \
               "WHERE   session_id = %s " \
               "AND     node_type = %s"
        if activity:
            stmt += " AND activity = %s"
            self.__cursor.execute(stmt, (session_id, type_, activity))
        else:
            self.__cursor.execute(stmt, (session_id, type_))
        queryset = self.__cursor.fetchall()
        return [{"id": node[0],
                 "node": node[1],
                 "node_type": node[2],
                 "activity": node[3],
                 "longitude": node[4],
                 "latitude": node[5]} for node in queryset]

    def get_session_plan_vehicle_route(self, session_user_id):

        stmt = "SELECT	id, " \
               "        node_i, " \
               "        N1.longitude, " \
               "        N1.latitude, " \
               "        node_j, " \
               "        N2.longitude, " \
               "        N2.latitude, " \
               "        vehicle_id " \
               "FROM	rs_sessionplanvehicleroute " \
               "INNER JOIN " \
               "        nodes N1 " \
               "ON      node_i = N1.node_id " \
               "INNER JOIN " \
               "        nodes N2 " \
               "ON      node_j = N2.node_id " \
               "WHERE	vehicle_id = " \
               "        ( " \
               "        SELECT	vehicle_id " \
               "        FROM	rs_sessionuservehicle " \
               "        WHERE	user_id = %s" \
               "        )"
        self.__cursor.execute(stmt, (session_user_id,))
        queryset = self.__cursor.fetchall()

        return [{"id": node[0],
                 "node_i": node[1],
                 "node_i_longitude": node[2],
                 "node_i_latitude": node[3],
                 "node_j": node[4],
                 "node_j_longitude": node[5],
                 "node_j_latitude": node[6],
                 "vehicle_id": node[7]} for node in queryset]

    def get_session_users_vehicle(self, session_user_id):

        stmt = "SELECT	" + ', '.join(FIELDS_SESSION_USER) + " " \
               "FROM	rs_sessionuservehicle " \
               "INNER JOIN " \
               "        rs_sessionuser " \
               "ON      rs_sessionuservehicle.user_id = rs_sessionuser.id " \
               "INNER JOIN" \
               "        nodes " \
               "ON      origin = node_id " \
               "WHERE	vehicle_id = " \
               "        ( " \
               "        SELECT	vehicle_id" \
               "        FROM	rs_sessionuservehicle" \
               "        WHERE	user_id = %s" \
               "        )"
        self.__cursor.execute(stmt, (session_user_id,))
        queryset = self.__cursor.fetchall()

        return [map_record_session_user(user) for user in queryset]
