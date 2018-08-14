"""
Test the accuracy of function frm_corr.
"""

import numpy as np
from sh.frm import *

b = 4

val = 0.
step = 1.
for n in xrange(1):
	val += step
	f = np.array([i+1 for i in xrange(4*b**2)])
	# f = [val+i*step for i in xrange(4*b**2)]
	# f = np.random.randn(4*b**2)
	# f = np.random.randint(1, 100, 4*b**2)

	# f = (f - np.mean(f))/np.std(f)

	g = [1. for i in f]
	# g = np.random.randn(4*b**2)

	# print np.max(f), np.mean(f), np.min(f), np.std(f), np.sum(f)
	print frm_corr(f,f).max(), frm_corr(f**2,g).max()