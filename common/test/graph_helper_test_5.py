from grid_digraph_generator import GridDigraphGenerator

if __name__ == '__main__':
    gh = GridDigraphGenerator()
    graph = gh.generate(5, 5)
    print graph.get_capacities()
