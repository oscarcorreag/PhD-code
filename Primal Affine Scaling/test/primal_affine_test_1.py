import scipy.io
from scipy.sparse import csr_matrix
import scipy
import time
import numpy as np

from primal_affine import PrimalAffine


def mat_parse(file):
    mat_content = scipy.io.loadmat(file)
    mat_struct = mat_content['Problem']
    val = mat_struct[0, 0]
    A = csr_matrix(val['A']).todense()
    b = val['b']
    c = val['aux'][0][0][0]
    return A, b, c


if __name__ == '__main__':
    # http://www.cise.ufl.edu/research/sparse/mat/LPnetlib/
    A, b, c = mat_parse('lp_agg.mat')

    print(np.shape(A))
    print(np.shape(b))
    print(np.shape(c))

    # t1 = time.perf_counter()
    t1 = time.clock()
    primal = PrimalAffine(c, A, b, opt_gap=1e-6)
    # elapsed = (time.perf_counter() - t1)
    elapsed = (time.clock() - t1)
    print(elapsed)
    primal.results()
