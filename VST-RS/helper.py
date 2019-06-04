import numpy as np


def assign_users_to_pois(graph, users, pois, method, seed=0, k=3):
    requests = []
    if method == "Voronoi":
        groups, _ = graph.get_voronoi_medoids_cells(pois, users)
        for p, group in groups.iteritems():
            requests.extend([(u, p) for u in group])
    elif method == "random":
        np.random.seed(seed)
        for u in users:
            p = pois[np.random.randint(0, len(pois))]
            requests.append((u, p))
    elif method == "k-closest":
        np.random.seed(seed)
        for u in users:
            k_closest = graph.get_k_closest_destinations(u, k, pois)
            p = pois[np.random.randint(0, len(k_closest))]
            requests.append((u, p))
    else:
        raise (RuntimeError, "Method " + method + " not implemented!")
    return requests

