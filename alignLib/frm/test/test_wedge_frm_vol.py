"""
Test the frm_constrained_corr function on a whole volume with missing wedge problem.
"""

from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import Timing

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
b = 16
v2 = vol(v)

wedge = np.array(create_wedge_sf(-60, 60, b))
m1 = np.ones(4*b**2)

for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)
	rotateSpline(v, v2, phi, psi, the)

	res = np.zeros((2*b, 2*b, 2*b))
	res2 = np.zeros((2*b, 2*b, 2*b))

	for r in xrange(1, 10):
		sf = np.array(vol2sf(v, r, b))
		sf2 = np.array(vol2sf(v2, r, b))
		sf2 = sf2 * wedge

		res += frm_corr(sf2, sf) * r**2
		res2 += frm_constrained_corr(sf2, wedge, sf, m1) * r**2
	
	ang = frm_find_best_angle(res, b)
	ang2 = frm_find_best_angle(res2, b)

	print rotation_distance([phi, psi, the], ang), rotation_distance([phi, psi, the], ang2)