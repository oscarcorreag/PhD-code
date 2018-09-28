from math import log


def bpr(edges, load, cap, alpha=0.15, beta=4.0):
    new_weights = dict()
    for e, weight in edges.iteritems():
        rl = 0.0
        if e in load and e in cap:
            if load[e] > 0 and cap[e] > 0:
                rl = float(load[e]) / cap[e]
        new_weights[e] = weight * (1 + alpha * rl ** beta)
    return new_weights


def bpr_log(edges, load, cap, alpha=0.15, beta=4.0):
    new_weights = dict()
    for e, weight in edges.iteritems():
        rl = 0.0
        if e in load and e in cap:
            if load[e] > 0 and cap[e] > 1:
                rl = log(load[e]) / log(cap[e])
        new_weights[e] = weight * (1 + alpha * rl ** beta)
    return new_weights

