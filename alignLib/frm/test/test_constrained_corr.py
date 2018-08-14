"""
Test the accuracy of frm_constrained_corr function.
Be careful with the actual meaning of the operation *, in this case holds: f * f < f^2 * m.
"""

import numpy as np
from sh.frm import *

b = 4

# f = np.random.randint(1, 100, 4*b**2)
f = np.array([i for i in xrange(4*b**2)])
# np.random.shuffle(f)
# f = f - np.mean(f)
# g = np.random.randint(1, 100, 4*b**2)
# g = np.array([i for i in xrange(4*b**2)])

m1 = np.ones(4*b**2)
m2 = np.ones(4*b**2)

# print frm_corr(f,g).max(), (frm_corr(f*m1, g*m2)/frm_corr(m1, m2)).max()
# print frm_corr(f,g).max(), frm_constrained_corr(f, m1, g, m2).max()
print np.mean(f)**2*4*np.pi
print frm_corr(f, f).max()