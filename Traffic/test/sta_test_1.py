from digraph import Digraph
from sta import STA


if __name__ == '__main__':
    graph = Digraph(capacitated=True)
    graph.append_edge_2((0, 1), weight=.56, capacity=1000)
    graph.append_edge_2((0, 2), weight=1, capacity=1000)
    graph.append_edge_2((1, 2), weight=.56, capacity=1000)
    O_D = {(0, 2): 1000}
    sta = STA(graph)
    sta.all_or_nothing(O_D, log_history=True)
