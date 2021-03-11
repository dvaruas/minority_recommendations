# Taken from https://github.com/frbkrm/HomophilicNtwMinorities/blob/master/estimate_empirical_homophily/estimate_homophily_empirical.py
import numpy as np
from scipy.optimize import fsolve


def equations(p, *args):
    minority_fraction, min_min, maj_maj, maj_min, root_num = args
    fb = 1 - minority_fraction
    fa = minority_fraction

    h_aa, h_bb, ca, beta_a, beta_b = p

    M = maj_maj + maj_min + min_min
    m_bb = maj_maj
    m_ab = maj_min
    m_aa = min_min

    pbb = float(m_bb) / (m_bb + m_ab + m_aa)
    paa = float(m_aa) / (m_aa + m_ab + m_bb)
    pba = float(m_ab) / (m_aa + m_bb + m_ab)
    pab = pba

    h_ab = 1- h_aa
    h_ba = 1- h_bb

    A = (h_aa - h_ab) * (h_ba - h_bb)
    B = ((2 * h_bb - (1 - fa) * h_ba) * (h_aa - h_ab) + (2 * h_ab - fa * (2 * h_aa - h_ab)) * (h_ba - h_bb))
    C = (2 * h_bb * (2* h_ab - fa * (2 * h_aa - h_ab)) - 2 * fa * h_ab * (h_ba - h_bb) - 2 * (1 - fa)* h_ba * h_ab)
    D = - 4 * fa * h_ab * h_bb
    P = [A, B, C, D]

    K = beta_b / (beta_a + beta_b)
    Z = 1 - K

    return ((pbb * ((fb * h_bb * K) + (fa * (1 - h_bb) * Z))) - (fb**2 * h_bb * K),
            (paa * ((fa * h_aa * Z) + (fb * (1 - h_aa) * K))) - (fa**2 * h_aa * Z ),
            beta_a - float(fa * h_aa) / (h_aa * ca + h_ab * (2 - ca)) - float(fb * h_ba) / (h_ba * ca + h_bb * (2 - ca)),
            beta_b - float(fb * h_bb) / (h_ba * ca + h_bb * (2 - ca)) - float(fa * h_ab) / (h_aa * ca + h_ab * (2 - ca)),
            ca - np.roots(P)[root_num])


def homophily_estimate(minority_fraction, min_min_edges, maj_maj_edges, min_maj_edges):
    h_aa, h_bb = None, None
    for root_num in [0,1,2]:
        arg_pack = (minority_fraction, min_min_edges, maj_maj_edges, min_maj_edges, root_num)
        h_aa_anal, h_bb_anal, ca, beta_a, beta_b = fsolve(equations, (1, 1, 0.5, 0.5, 0.5), args=arg_pack)
        degree_exponent_a = float(1) / beta_a + 1
        degree_exponent_b = float(1) / beta_b + 1
        if ca >= 0.0 and ca <= 2.0:
            if h_aa_anal >= 0.0 and h_aa_anal <= 1.0 and h_bb_anal >= 0.0 and h_bb_anal <= 1.0:
                if h_aa != None and h_bb != None:
                    # Some value has already been set, multiple values found, quit!
                    return (None, None)
                h_aa = h_aa_anal
                h_bb = h_bb_anal

    return (h_aa, h_bb)
