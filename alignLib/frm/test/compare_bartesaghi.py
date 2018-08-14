"""
Compare with Bartesaghi's way of normalization.
"""

from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import timing

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
r = 8
b = 32
v2 = vol(v)
wedge = np.array(create_wedge_sf(-45, 45, b))

def bart_way(f, mf, g, mg):
    if f.__class__ != np.array:
        f = np.array(f, dtype='double')
    if mf.__class__ != np.array:
        mf = np.array(mf, dtype='double')
    if g.__class__ != np.array:
        g = np.array(g, dtype='double')
    if mg.__class__ != np.array:
        mg = np.array(mg, dtype='double')
    
    dummy1 = frm_corr(f*mf, g*mg)
    dummy2 = frm_corr(f**2*mf, mg)
    dummy3 = frm_corr(mf, g**2*mg)
    dummy4 = frm_corr(mf, mg)

    res = dummy1 / ((dummy2 * dummy3)**0.5 * dummy4)

    return res

dist = []
dist2 = []
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)
	rotateSpline(v, v2, phi, psi, the) 

	sf = vol2sf(v, r, b)
	sf = sf * wedge
	sf2 = vol2sf(v2, r, b)
	sf2 = sf2 * wedge

	res = bart_way(sf2, wedge, sf, wedge)
	ang = frm_find_best_angle(res, b)
	dist.append(rotation_distance([phi, psi, the], ang))

	res = frm_constrained_corr(sf2, wedge, sf, wedge)
	ang = frm_find_best_angle(res, b)
	dist2.append(rotation_distance([phi, psi, the], ang))

	print dist[-1], dist2[-1]

print 'Diff: ', np.max(dist), np.mean(dist), np.min(dist), np.std(dist)
print 'Diff2: ', np.max(dist2), np.mean(dist2), np.min(dist2), np.std(dist2)