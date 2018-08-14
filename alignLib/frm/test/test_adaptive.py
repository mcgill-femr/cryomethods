"""
Test the adaptive bandwidth approach vs. fixed bandwidth
"""

from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import timing
from pytom.basic.structures import WedgeInfo


v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
v2 = vol(v)

w = np.array(create_wedge_sf(-60, 60, 32))
m = np.ones(4*32**2)

wedge = WedgeInfo(30.0)

def frm_fourier_constrained_vol(vf, mf, vg, mg):
    radius = vf.sizeX()/2-3 # intepolation in the outer part is nonsense
    b = 32
    
    from pytom.basic.fourier import fft, ifft, ftshift, iftshift

    vf = ftshift(reducedToFull(fft(iftshift(vf, inplace=False))), inplace=False)
    vg = ftshift(reducedToFull(fft(iftshift(vg, inplace=False))), inplace=False)

    vfr = real(vf)
    vfi = imag(vf)
    vgr = real(vg)
    vgi = imag(vg)

    res = np.zeros((2*b, 2*b, 2*b))
    for r in xrange(1, radius+1):
        corr = frm_fourier_constrained_corr(vol2sf(vfr, r, b), vol2sf(vfi, r, b), mf, vol2sf(vgr, r, b), vol2sf(vgi, r, b), mg, True)
        res += corr*(r**2)
    
    return res

diff_old = []
diff_new = []
total_time1 = 0.0
total_time2 = 0.0

# mean0std1(v)
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)

	# print [phi, psi, the]
	
	rotateSpline(v, v2, phi, psi, the)
	v2 = wedge.apply(v2)
	
	t = timing()

	# 1 method
	t.start()
	res = frm_fourier_adaptive_wedge_vol(v2, [-60, 60], v, [-90, 90], [4, 32], v.sizeX()/2-3)
	ang = frm_find_best_angle(res, 32)
	t1 = t.end()

	dist_old = rotation_distance([phi, psi, the], ang)
	diff_old.append(dist_old)
	total_time1 += t1
	
	# 2 method
	t.start()
	res = frm_fourier_constrained_vol(v2, w, v, m)
	ang2 = frm_find_best_angle(res, 32)
	t2 = t.end()
	
	dist_new = rotation_distance([phi, psi, the], ang2)
	diff_new.append(dist_new)
	total_time2 += t2

	print dist_old, dist_new
	
print diff_old
print diff_new
print total_time1/100, total_time2/100
