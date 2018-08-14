"""
Test the result consistency of SOFT with FRM.
"""

import numpy as np
from sh.soft import *
from sh.frm import *
from pytom.tools.maths import rotation_distance
from pytom_volume import *
from sh.vol2sf import vol2sf

b = 16

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
v2 = vol(v)
r = 8
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)

	f = vol2sf(v, r, b)
	rotateSpline(v, v2, phi, psi, the)
	g = vol2sf(v2, r, b)

	# 1. the soft way
	res = soft_corr(g, f)
	ang = soft_find_best_angle(res, b)

	# 2. the frm way
	# res = frm_corr(g, f)
	# ang2 = frm_find_best_angle(res, b)

	print rotation_distance(ang, [phi, psi, the]) #, rotation_distance(ang2, [phi, psi, the]), rotation_distance(ang, ang2)
