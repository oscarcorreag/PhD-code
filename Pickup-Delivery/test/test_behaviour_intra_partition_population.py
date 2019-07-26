import operator
import math
import csv
import time

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from numpy.random import RandomState


if __name__ == '__main__':
    osm = OsmManager()
    generator = SuitableNodeWeightGenerator()
    #
    regions = {
        'MEL': (
            [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727],
            ['COLES', 'WOOLWORTHS', 'ALDI']
        ),
        # 'UIO': (
        #     [-78.57160966654635, -0.4180073651030667, -78.36973588724948, -0.06610523586538203],
        #     ['LA FAVORITA', 'SANTA MARIA', 'MI COMISARIATO']
        # ),
        # 'MHT': (
        #     [-74.0326191484375, 40.69502239217181, -73.93236890429688, 40.845827729757275],
        #     ['WALMART', 'TARGET', 'COSTCO']
        # ),
    }

    delta_meters = 5000.0
    delta = delta_meters / 111111
    num_samples = 5
    customer_densities = range(5, 11)
    ratio_customers_drivers = 2.0
    f = .5
    #
    results = []
    seed = 0
    for region, info in regions.iteritems():
        for customer_density in customer_densities:
            sample = 0
            while sample < num_samples:
                # Setup random object.
                seed += 1
                rnd = RandomState(seed)
                # Compute bbox coordinates.
                min_lon = rnd.uniform(info[0][0], info[0][2] - delta)
                min_lat = rnd.uniform(info[0][1], info[0][3] - delta)
                max_lon = min_lon + delta
                max_lat = min_lat + delta
                # Generate network sample.
                graph, _, _, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                                hotspots=False, poi_names=info[1])
                # Get biggest component within graph and consider it the new graph.
                components = graph.get_components()
                if len(components) > 1:
                    sizes = {component: len(nodes) for component, nodes in components.iteritems()}
                    nodes = components[max(sizes.iteritems(), key=operator.itemgetter(1))[0]]
                    graph = graph.extract_node_induced_subgraph(nodes)
                # Network size.
                N = len(graph.keys())
                if N < delta_meters / 10:
                    continue
                # Sample as many customers as the current customer density requires.
                num_customers = int(math.floor(customer_density / 100. * N))
                customers = set(rnd.choice(a=list(graph.keys()), size=num_customers, replace=False))
                # Sample as many drivers as the constant ratio requires.
                num_drivers = int(math.floor(num_customers / ratio_customers_drivers))
                free = set(graph.keys()).difference(customers)
                d_starts_ends = rnd.choice(a=list(free), size=num_drivers * 2, replace=False)
                drivers = [(d_starts_ends[i], d_starts_ends[i + num_drivers]) for i in range(num_drivers)]
                # Compute drivers' shortest paths and their distances.
                graph.compute_dist_paths(pairs=drivers)
                sorted_dist = {(start, end): graph.dist[tuple(sorted([start, end]))] for start, end in drivers}
                sorted_dist = sorted(sorted_dist.iteritems(), key=operator.itemgetter(1))
                # Compute partitions for drivers and retrieve number of customers within them.
                taken = set()
                for (start, end), dist in sorted_dist:
                    path = graph.paths[tuple(sorted([start, end]))]
                    customers_partition = set()
                    for i, vertex in enumerate(path):
                        # Explore graph from each intermediate vertex in driver's path until a constant fraction.
                        region = graph.explore_upto(vertex, dist * f)
                        # Which customers are in this region?
                        customers_region = customers.intersection(region.keys())
                        customers_partition.update(customers_region)
                    num_cust_part_before = len(customers_partition)
                    customers_partition = customers_partition.difference(taken)
                    taken.update(customers_partition)
                    num_customers_part = len(customers_partition)
                    normalized = num_customers_part / float(N)
                    results.append([customer_density, ratio_customers_drivers, f, normalized, num_customers_part,
                                    num_cust_part_before - num_customers_part])
                #
                sample += 1

    result_file = open("files/populations_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)

