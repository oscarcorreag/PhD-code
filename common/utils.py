import itertools
import math
import string

from numpy.random import RandomState


def id_generator(size=6, chars=string.ascii_uppercase + string.digits, seed=None):
    #
    rnd = RandomState()
    if seed is not None:
        rnd = RandomState(seed)
    #
    return ''.join(rnd.choice(list(chars)) for _ in range(size))


def comb(l, n):
    res = []
    l_ = list(l)
    if n == 1:
        for e in l_:
            res.append([e])
    else:
        for i in range(len(l_) - n + 1):
            for e in comb(l_[i + 1:], n - 1):
                t = [l_[i]]
                t.extend(e)
                res.append(t)
    return res


def comb_v(l, n, v):
    l.remove(v)
    res = comb(l, n - 1)
    for e in res:
        e.append(v)
    return res


def comb_upto_n(l, n):
    res = []
    for i in range(1, n + 1):
        res.extend(comb(l, i))
    return res


def entropy(X):
    grouped = {k: len(list(v)) for k, v in itertools.groupby(sorted(X))}
    total = float(sum(grouped.values()))
    probs = [freq / total for freq in grouped.values()]
    return -1 * sum([prob * math.log(prob, 2) for prob in probs])


EARTH_RADIUS = 6371000


def haversine(lat1, lon1, lat2, lon2):
    lat_rad_1 = math.radians(lat1)
    lat_rad_2 = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2) * math.sin(delta_lat / 2) + math.cos(lat_rad_1) * math.cos(lat_rad_2) * math.sin(
        delta_lon / 2) * math.sin(delta_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c


def divisors(k):
    divs = [i for i in range(2, int(math.ceil(k / 2.)) + 1) if k % i == 0]
    return divs


def num_partitions(k):
    while 1:
        divs = divisors(k)
        if divs:
            break
        k += 1
    n_divs = len(divs)
    i = int(math.ceil(n_divs / 2.)) - 1
    np1 = divs[i]
    np2 = k / np1
    return k, np1, np2


def corners(i, j, m, n, np1, np2, off1, off2):
    c_nw = i * off2 * m + j * off1
    if i < np2 - 1:
        c_sw = i * off2 * m + (off2 - 1) * m + j * off1
    else:
        c_sw = i * off2 * m + (n - (np2 - 1) * off2 - 1) * m + j * off1
    if j < np1 - 1:
        c_ne = c_nw + off1 - 1
        c_se = c_sw + off1 - 1
    else:
        c_ne = c_nw + m - (np1 - 1) * off1 - 1
        c_se = c_sw + m - (np1 - 1) * off1 - 1
    return c_nw, c_ne, c_sw, c_se


def divide_grid_graph(dims, num_zones):
    m = dims[0]
    n = dims[1]
    num_zones_, np1, np2 = num_partitions(num_zones)
    off1 = int(float(m) / np1)
    off2 = int(float(n) / np2)
    zones = {}
    for i in range(np2):
        for j in range(np1):
            c_nw, c_ne, c_sw, _ = corners(i, j, m, n, np1, np2, off1, off2)
            start = c_nw
            end = c_ne
            zone = []
            while start <= c_sw:
                zone.extend(range(start, end + 1))
                start += m
                end += m
            zones[(i, j)] = zone
    return num_zones_, np1, np2, zones


def merge_two_zones(zones, np1, np2, seed=None):
    #
    rnd = RandomState()
    if seed is not None:
        rnd = RandomState(seed)
    #
    i = rnd.choice(a=range(0, np2))
    j = rnd.choice(a=range(0, np1))
    i_ = i
    j_ = j
    dir_ = rnd.choice(a=[0, 1])
    if dir_ == 0:
        if 0 < i < np2 - 1:
            i_ = rnd.choice(a=[i - 1, i + 1])
        elif i == 0:
            i_ = 1
        else:
            i_ = i - 1
    else:
        if 0 < j < np1 - 1:
            j_ = rnd.choice(a=[j - 1, j + 1])
        elif j == 0:
            j_ = 1
        else:
            j_ = j - 1
    zones_ = {k: nodes for k, nodes in zones.iteritems() if k != (i, j) and k != (i_, j_)}
    new_zone = list(zones[(i, j)])
    new_zone.extend(zones[i_, j_])
    zones_["m"] = new_zone
    return zones_


def assign_query_to_poi(nq, npq, seed=None):
    #
    rnd = RandomState()
    if seed is not None:
        rnd = RandomState(seed)
    pois = []
    for i in range(nq):
        pois.extend([i] * npq)
    rnd.shuffle(pois)
    return pois


def distribute_pois_in_queries(dims, nq, npq, seed=None):
    #
    rnd = RandomState()
    if seed is not None:
        rnd = RandomState(seed)
    # Compute number of POIs per zone.
    P = nq * npq
    s = rnd.zipf(a=2., size=P)
    ppz = sorted([len(list(v)) for _, v in itertools.groupby(sorted(s))])
    nz = len(ppz)
    # Divide graph into zones.
    nz_, np1, np2, zones = divide_grid_graph(dims, nz)
    # Merge two zones if needed.
    zones_ = dict(zones)
    if nz != nz_:
        zones_ = merge_two_zones(zones, np1, np2, seed=seed)
    # Assign number of POIs to each zone.
    npz = dict()
    if "m" in zones_:  # Two zones were merged.
        npz["m"] = ppz[-1]  # Assign to zone "m" the largest number of POIs which is at the last position.
        zone_keys = [k for k in zones_ if k != "m"]
    else:
        zone_keys = list(zones_.keys())
    rnd.shuffle(zone_keys)
    for i, k in enumerate(zone_keys):
        npz[k] = ppz[i]
    # Locate POIs within each zone.
    qpp = assign_query_to_poi(nq, npq, seed=seed)
    ppq = dict()
    w = 0
    for k, nodes in zones_.iteritems():
        pois = rnd.choice(a=nodes, size=npz[k], replace=False)
        # Assign which query each POI belongs to.
        ass = zip(qpp[w:w + npz[k]], pois)
        for q, p in ass:
            try:
                ppq[q].append(p)
            except KeyError:
                ppq[q] = [p]
        w += npz[k]
    return ppq
