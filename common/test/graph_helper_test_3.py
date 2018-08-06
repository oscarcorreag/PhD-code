from grid_digraph_generator import GridDigraphGenerator

if __name__ == '__main__':
    gh = GridDigraphGenerator()
    graph = gh.generate(10, 10)
    print graph.get_edges()
