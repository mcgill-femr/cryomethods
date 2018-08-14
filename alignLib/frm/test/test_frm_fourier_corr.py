"""
Test the accuracy of frm_fourier_corr function.
"""

from pytom_volume import *
from pytom.basic.fourier import *
import numpy as np
from sh.soft import *
from sh.frm import *
from pytom.tools.maths import rotation_distance
from sh.vol2sf import vol2sf

from pytom.basic.fourier import fft, ftshift, iftshift
from pytom_volume import reducedToFull
from pytom_volume import real, imag

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/binning/tempProteasome_bin2.em')
v2 = vol(v)

b = 16
r = 4

m = np.ones(4*b**2)
# w = m
w = create_wedge_sf(-60, 60, b)

dist = []
dist2 = []
dist3 = []
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)

	fv1 = ftshift(reducedToFull(fft(iftshift(v, inplace=False))), inplace=False)

	# 1. rotate in real space and use the frm_fourier_corr to find the angle
	# This is the least accurate way, since the interpolation happens in real space.
	# rotateSpline(v, v2, phi, psi, the)
	# fv2 = ftshift(reducedToFull(fft(iftshift(v2))))
	# res = frm_fourier_corr(vol2sf(real(fv2), r, b), vol2sf(imag(fv2), r, b), vol2sf(real(fv1), r, b), vol2sf(imag(fv1), r, b))

	# 2. rotate real and imag parts seperately and feed into the frm_fourier_corr
	fr = real(fv1)
	fi = imag(fv1)

	# rotateSpline(v, v2, phi, psi, the)
	# fv2 = ftshift(reducedToFull(fft(iftshift(v2))))
	# fr2 = real(fv2)
	# fi2 = imag(fv2)
	fr2 = vol(fr); rotateSpline(fr, fr2, phi, psi, the)
	fi2 = vol(fi); rotateSpline(fi, fi2, phi, psi, the)

	fr = np.array(vol2sf(fr, r, b))
	fi = np.array(vol2sf(fi, r, b))
	fr2 = np.array(vol2sf(fr2, r, b))
	fi2 = np.array(vol2sf(fi2, r, b))

	fr2 = fr2 * w
	fi2 = fi2 * w

	res = frm_fourier_corr(fr2, fi2, fr, fi, return_real=True)

	# 3. add two volumes and get the final result
	# res = frm_constrained_corr(fr2, w, fr, m) + frm_constrained_corr(fi2, w, fi, m)
	
	ang = frm_find_best_angle(res, b)
	dist.append(rotation_distance(ang, [phi, psi, the]))

	# 4. compare with the constrained version
	res = frm_fourier_constrained_corr(fr2, fi2, w, fr, fi, m, return_real=True)

	ang2 = frm_find_best_angle(res, b)
	dist2.append(rotation_distance(ang2, [phi, psi, the]))

	# 5. do it in the soft way
	# res = soft_fourier_corr(fr2, fi2, fr, fi, return_real=True)
	res = soft_fourier_constrained_corr(fr2, fi2, w, fr, fi, m, return_real=True)

	ang3 = soft_find_best_angle(res, b)
	dist3.append(rotation_distance(ang3, [phi, psi, the]))

	print dist[-1], dist2[-1], dist3[-1]

print np.max(dist), np.mean(dist), np.min(dist), np.std(dist)
print np.max(dist2), np.mean(dist2), np.min(dist2), np.std(dist2)
print np.max(dist3), np.mean(dist3), np.min(dist3), np.std(dist3)