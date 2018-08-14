"""
Test the frm_constrained_corr under the present of missing wedge problem.
"""

from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import timing

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/binning/tempProteasome_bin2.em')
r = 8
b = 32
v2 = vol(v)
# wedge = np.ones(4*b**2)
wedge = np.array(create_wedge_sf(-60, 60, b))
m1 = np.ones(4*b**2)

# print wedge
# print np.sum(wedge)/np.sum(m1)

t = timing()

t.start()

dist = []
dist2 = []
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)
	rotateSpline(v, v2, phi, psi, the) # you cannot expect very high accuracy, since we are using spline interpolation here

	sf = np.array(vol2sf(v, r, b))
	sf = sf * wedge
	sf2 = np.array(vol2sf(v2, r, b))
	sf2 = sf2 * wedge

	res = frm_corr(sf2, sf)
	ang = frm_find_best_angle(res, b)
	dist.append(rotation_distance([phi, psi, the], ang))

	res = frm_constrained_corr(sf2, wedge, sf, wedge)
	ang = frm_find_best_angle(res, b)
	dist2.append(rotation_distance([phi, psi, the], ang))

# print 'Diff: ', np.max(dist), np.mean(dist), np.min(dist), np.std(dist)
# print 'Diff2: ', np.max(dist2), np.mean(dist2), np.min(dist2), np.std(dist2)

print dist
print dist2

print t.end()