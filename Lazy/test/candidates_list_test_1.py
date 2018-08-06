import time

from canditates_list import CandidatesList

if __name__ == '__main__':
    start_time = time.clock()
    for _ in xrange(600):
        cl = CandidatesList(300)
        for i in xrange(300):
            cl.append(i)
    print("elapsed time:", time.clock() - start_time)
