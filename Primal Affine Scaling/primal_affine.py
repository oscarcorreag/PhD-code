import numpy as np
import pandas as pd
import math
import numba


class PrimalAffine(object):
    def __init__(self, c, a, b, opt_gap=1.0e-6, eps=1.0e-12, rho=0.95, m=None):
        self.c = c
        self.a = a
        self.b = b
        self.opt_gap = opt_gap
        self.eps = eps
        self.rho = rho
        self._alphas = []
        self._f_values = []
        self._gaps = []
        self._iter = []
        self._pre_check()

        if m is None:
            self.m = 100 * np.max(abs(self.c))
        else:
            self.m = m
        print("Max value = {}".format(np.max(abs(self.c))))
        print("Big-M = {}".format(self.m))

        self._optimize_primal()

    def _pre_check(self):
        if not (isinstance(self.a, np.ndarray) or isinstance(self.b, np.ndarray) or isinstance(self.c, np.ndarray)):
            raise Exception('Inputs must be a numpy arrays')

    def _check(self, ra, ca, rb, rc):
        if np.linalg.matrix_rank(self.a) != ra:
            raise Exception('Matrix A is not full rank')

        if rb != ra:
            if np.size(self.b) == ra:
                self.b = np.transpose(self.b)
            else:
                raise AttributeError('dimension of vector b is not correct')

        if rc != ca:
            if np.size(self.c) == ca:
                self.c = np.transpose(self.c)
            else:
                raise AttributeError('dimension of vector b is not correct')

    def _optimize_primal(self):

        r_a, c_a = np.shape(self.a)
        r_b = np.shape(self.b)[0]
        r_c = np.shape(self.c)[0]

        self._check(r_a, c_a, r_b, r_c)

        x = np.ones((c_a, 1))
        a = np.c_[self.a, self.b - np.dot(self.a, x)]
        x = np.ones((c_a + 1, 1))
        c = np.vstack([self.c, self.m])
        d = np.eye(c_a + 1)
        y = self._compute_y(a, d, c)

        i = 0
        while self._dual_gap(c, x, self.b, y) > self.opt_gap:
            z = c - np.dot(np.transpose(a), y)
            dx = np.dot(-d, z)
            if np.all(dx >= 0):
                print('Unbounded problem')
                break
            alpha = self.rho * np.min(-x[dx < self.eps] / dx[dx < self.eps].ravel())
            x += alpha*dx
            d = np.diag(x.ravel())**2
            y = self._compute_y(a, d, c)
            i += 1

            f_obj = np.dot(np.transpose(c), x)
            self._f_values.append(f_obj.ravel()[0])
            self._alphas.append(alpha.ravel()[0])
            self._gaps.append(self._dual_gap(c, x, self.b, y).ravel()[0])

        if x[c_a] > 1e-5:
            print('Infeasible problem. x[n+1] = {}'.format(x[c_a]))
        else:
            pass
            print('\n', x[0:c_a])

    def _compute_y(self, aa, dd, cc):
        term1 = np.dot(np.dot(aa, dd), np.transpose(aa))
        term2 = np.dot(np.dot(aa, dd), cc)
        L = self._chol_semidefinite(term1)
        sol = self._chol_solve(L, term2)
        return sol

    @staticmethod
    def _dual_gap(cc, xx, bb, yy):
        term1 = np.dot(np.transpose(cc), xx)
        term2 = term1 - np.dot(np.transpose(bb), yy)
        term3 = 1.0 + abs(term1)
        return abs(term2)/term3

    @staticmethod
    @numba.autojit
    def _chol_semidefinite(A):
        n = len(A)

        # create zero matrix for L
        L = np.zeros((n, n))

        # Perform the Cholesky decomposition
        for i in range(n):
            for k in range(i+1):
                tmp_sum = 0
                for j in range(k):
                    tmp_sum += L[i, j] * L[k, j]

                if i == k:  # diagonal
                    L[i, k] = math.sqrt(A[i, i] - tmp_sum)
                    if L[i, k] <= 0:
                        L[i, k] = 10**10

                else:
                    L[i, k] = (1.0 / L[k, k] * (A[i, k] - tmp_sum))
        return L

    @staticmethod
    def _chol_solve(L, b):
        L_inv = np.linalg.inv(L)
        z = np.dot(L_inv, b)
        y = np.dot(np.transpose(L_inv), z)
        return y


    def results(self):
        d = {'gap': self._gaps, 'fobj': self._f_values, 'alpha': self._alphas}
        df = pd.DataFrame(d)
        print(df)