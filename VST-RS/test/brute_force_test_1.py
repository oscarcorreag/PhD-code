import time

from grid_digraph_generator import GridDigraphGenerator
from brute_force import BruteForce


if __name__ == '__main__':

    m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)

    terminals = [88, 66, 77, 5, 33, 53, 71]
    pois = [65, 12]

    db_woc = BruteForce(graph)
    start_time = time.clock()
    db_woc.steiner_forest(terminals, pois, 4)
    elapsed_time = time.clock() - start_time
