if __name__ == '__main__':
    predecessors_by_driver = \
        {(21, 13): {13: [18], 18: [17, 24], 24: [27, 5, 18], 17: [21], 27: [24], 5: [6, 24], 6: [5]}}
    for (s_v, e_v), predecessors in predecessors_by_driver.iteritems():
        route = [e_v]
        while route[-1] != s_v:
            ps = predecessors[route[-1]]
            i = 0
            if len(ps) > 1:
                while route[-1] not in predecessors[ps[i]]:
                    i += 1
            route.append(ps[i])
            del ps[i]
        print route
