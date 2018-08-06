import pg8000

from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import make_parser


class Node:

    def __init__(self, id_, latitude, longitude):
        self.id = id_
        self.latitude = latitude
        self.longitude = longitude
        self.tags = {}


class Way:

    def __init__(self, id_):
        self.id = id_
        self.nodes = []
        self.tags = {}


class OsmHandler(ContentHandler):

    def __init__(self, user, password, database):
        ContentHandler.__init__(self)
        self.__levels = []
        self.nodes = {}
        self.ways = {}
        self.__current_node_id = None
        self.__current_way_id = None

        self.__conn = pg8000.connect(user=user, password=password, database=database)
        self.__cursor = self.__conn.cursor()
        self.__ord_way_nodes = 0

    def startDocument(self):
        print("startDocument")

    def startElement(self, name, attrs):

        if name == "node" and len(self.__levels) > 0 and self.__levels[-1] == "osm":
            self.__current_node_id = attrs["id"]
            self.nodes[self.__current_node_id] = Node(self.__current_node_id, attrs["lat"], attrs["lon"])
            self.__cursor.execute("INSERT INTO nodes VALUES (%s, %s, %s)", (self.__current_node_id, attrs["lat"], attrs["lon"]))

        if name == "tag" and len(self.__levels) > 0 and self.__levels[-1] == "node":
            self.nodes[self.__current_node_id].tags[attrs["k"]] = attrs["v"]
            self.__cursor.execute("INSERT INTO node_tags VALUES (%s, %s, %s)", (self.__current_node_id, attrs["k"], attrs["v"]))

        if name == "way" and len(self.__levels) > 0 and self.__levels[-1] == "osm":
            self.__current_way_id = attrs["id"]
            self.ways[self.__current_way_id] = Way(self.__current_way_id)
            self.__cursor.execute("INSERT INTO ways VALUES (" + str(self.__current_way_id) + ")")

        if name == "nd" and len(self.__levels) > 0 and self.__levels[-1] == "way":
            self.ways[self.__current_way_id].nodes.append(attrs["ref"])
            self.__ord_way_nodes += 1
            self.__cursor.execute("INSERT INTO way_nodes VALUES (%s, %s, %s)", (self.__current_way_id, attrs["ref"], self.__ord_way_nodes))

        if name == "tag" and len(self.__levels) > 0 and self.__levels[-1] == "way":
            self.ways[self.__current_way_id].tags[attrs["k"]] = attrs["v"]
            self.__cursor.execute("INSERT INTO way_tags VALUES (%s, %s, %s)", (self.__current_way_id, attrs["k"], attrs["v"]))

        if len(self.__levels) == 0 or (len(self.__levels) > 0 and self.__levels[-1] != name):
            self.__levels.append(name)

    def endElement(self, name):
        if self.__levels[-1] != name:
            raise AssertionError
        self.__levels.pop(-1)

    def endDocument(self):
        print("endDocument")
        self.__conn.commit()


class OsmParser:

    @staticmethod
    def parse(osmfile, user, password, database):

        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        handler = OsmHandler(user, password, database)
        parser.setContentHandler(handler)
        parser.parse(osmfile)

        print("number of nodes:", len(handler.nodes.keys()))
        print("number of ways:", len(handler.ways.keys()))
