"""
Test the new approach on a missingw wedge effected volume.
"""

from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import timing
from pytom.basic.structures import WedgeInfo
from pytom.localization.extractPeaks import extractPeaks
from pytom.angles.fromFile import AngleListFromEM
from pytom.basic.normalise import mean0std1
from pytom.simulation.whiteNoise import add
from pytom.basic.correlation import nxcc

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
b = 32
v2 = vol(v)

w = np.array(create_wedge_sf(-60, 60, b))
m = np.ones(4*b**2)

mask = read('/fs/home/ychen/matlab/test_frm/mask_11.em')
wedge = WedgeInfo(30.0)
angles = AngleListFromEM("")
angles.readRotationsFromEMFile("angles_12.85_7112.em")
# angles.readRotationsFromEMFile("angles_17.86_3040.em")

def frm_fourier_constrained_vol(vf, mf, vg, mg):
    radius = vf.sizeX()/2-3 # intepolation in the outer part is nonsense
    
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

mean0std1(v)
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)
	rotateSpline(v, v2, phi, psi, the)
	
	# apply wedge
	v2 = wedge.apply(v2)
	
	t = timing()

	# old method
	angles.reset()
	t.start()
	tmp = vol(v)
	peak = 0.0
	angle = angles.nextRotation()
	while angle != [None, None, None]:
		rotateSpline(v, tmp, angle[0], angle[1], angle[2])
		tmp = wedge.apply(tmp)
		res = nxcc(v2, tmp, mask)
		if res >= peak:
			peak = res
			ang = angle
		angle = angles.nextRotation()
	t1 = t.end()

	dist_old = rotation_distance([phi, psi, the], ang)
	# if dist_old > 30:
	# 	print [phi, psi, the], ang
	diff_old.append(dist_old)
	total_time1 += t1
	
	# new method
	t.start()
	res = frm_fourier_constrained_vol(v2, w, v, m)
	ang2 = frm_find_best_angle(res, b)
	t2 = t.end()

	dist_new = rotation_distance([phi, psi, the], ang2)
	diff_new.append(dist_new)
	total_time2 += t2

	print dist_old, dist_new
	
print diff_old
print diff_new
print total_time1/100, total_time2/100
