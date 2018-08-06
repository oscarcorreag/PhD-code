from shortest_path_lp import shortest_path_primal
from shortest_path_lp import shortest_path_dual
from grid_digraph_generator import GridDigraphGenerator
from digraph import Digraph
from networkx_graph_helper import NetworkXGraphHelper

if __name__ == '__main__':
    # graph = {'a': {'c': 14, 'd': 9, 'e': 15},
    #          'c': {'a': 14, 'f': 1},
    #          'd': {'a': 9, 'f': 11, 'g': 5, 'e': 3},
    #          'e': {'a': 15, 'd': 3, 'g': 15, 'h': 20},
    #          'f': {'c': 1, 'd': 11, 'g': 20, 'i': 1},
    #          'g': {'f': 20, 'd': 5, 'e': 15, 'h': 2, 'i': 30},
    #          'h': {'e': 20, 'g': 2, 'b': 3},
    #          'i': {'f': 1, 'g': 30, 'b': 1},
    #          'b': {'i': 1, 'h': 3}}

    gh = GridDigraphGenerator()
    graph = gh.generate(30, 30)
    terminals = [123, 464]

    distances_dual = shortest_path_dual(graph, terminals[0])

    distances, paths = shortest_path_primal(graph, terminals[0])

    ngh = NetworkXGraphHelper(graph)
    graph_path = Digraph()
    graph_path.append_from_path(paths[terminals[1]], graph)
    ngh.draw_graph(nodes_2=terminals,
                   subgraphs_2=[graph_path],
                   title_2="Primal: " + str(distances[terminals[1]]) + ", Dual: " + str(distances_dual[terminals[1]]))
