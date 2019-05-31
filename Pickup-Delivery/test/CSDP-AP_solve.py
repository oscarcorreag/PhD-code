from digraph import Digraph
from csdp_ap import CsdpAp


if __name__ == '__main__':
    graph = Digraph(undirected=False)

    graph.append_edge_2(('A', 'B'), weight=5)
    graph.append_edge_2(('A', 'C'), weight=6)
    graph.append_edge_2(('A', 'P2'), weight=9.5)
    graph.append_edge_2(('A', 'P3'), weight=3.5)
    graph.append_edge_2(('A', 'd'), weight=7)

    graph.append_edge_2(('B', 'A'), weight=5)
    graph.append_edge_2(('B', 'C'), weight=3.5)
    graph.append_edge_2(('B', 'P2'), weight=6)
    graph.append_edge_2(('B', 'P3'), weight=5.5)
    graph.append_edge_2(('B', 'd'), weight=3.6)

    graph.append_edge_2(('C', 'A'), weight=6)
    graph.append_edge_2(('C', 'B'), weight=3.5)
    graph.append_edge_2(('C', 'P1'), weight=4.5)
    graph.append_edge_2(('C', 'd'), weight=3)

    graph.append_edge_2(('P1', 'A'), weight=5)
    graph.append_edge_2(('P1', 'B'), weight=2)
    graph.append_edge_2(('P1', 'C'), weight=4.5)
    graph.append_edge_2(('P1', 'P2'), weight=6)
    graph.append_edge_2(('P1', 'P3'), weight=3.5)

    graph.append_edge_2(('P2', 'A'), weight=9.5)
    graph.append_edge_2(('P2', 'B'), weight=6)
    graph.append_edge_2(('P2', 'C'), weight=4.5)
    graph.append_edge_2(('P2', 'P1'), weight=6)

    graph.append_edge_2(('P3', 'A'), weight=3.5)
    graph.append_edge_2(('P3', 'B'), weight=5.5)
    graph.append_edge_2(('P3', 'C'), weight=6.5)
    graph.append_edge_2(('P3', 'P1'), weight=3.5)

    graph.append_edge_2(('o', 'A'), weight=2.5)
    graph.append_edge_2(('o', 'P1'), weight=3)
    graph.append_edge_2(('o', 'P2'), weight=8)
    graph.append_edge_2(('o', 'P3'), weight=2)
    graph.append_edge_2(('o', 'd'), weight=8)

    graph.append_edge_2(('d', 'B'), weight=3.6)
    graph.append_edge_2(('d', 'C'), weight=3)
    graph.append_edge_2(('d', 'P2'), weight=2.5)

    requests = [
        ([('P1', 1, 300)], ('A', 1, 300)),
        ([('P1', 1, 300)], ('B', 1, 300)),
        ([('P2', 1, 300), ('P3', 1, 300)], ('C', 1, 300))
    ]
    vehicles = [(('o', 1, 300), ('d', 1, 300))]
    csdp_ap = CsdpAp(graph)
    routes, cost = csdp_ap.solve(requests, vehicles, method='SP-based', partition_method='SP-Voronoi')
    print routes, cost
