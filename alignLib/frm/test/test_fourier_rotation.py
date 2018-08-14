"""
Test the accuracy of rotation in fourier space.
"""

from pytom_volume import *
from pytom_numpy import *
import numpy as np

from pytom.basic.fourier import fft, ftshift, iftshift, ifft
from pytom_volume import real, imag

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/temp80SRibosome.em')

# fv = vol_comp(32,32,17)
# fv.setAll(1+1j)
# for x in xrange(16,32,1):
#	for y in xrange(16,32,1):
#		for z in xrange(16):
#			fv(2+1j,x,y,z)
 	

# fv.setFtSizeX(32)
# fv.setFtSizeY(32)
# fv.setFtSizeZ(32)

# v = ifft(fv)
# v.write('v.em')


phi = 30
psi = 30
the = 30

# rotateSpline(v, v2, phi, psi, the)
# v2.write("real_rotated.em")

def fourier_rotate(v, phi, psi, the):
    vf = ftshift(reducedToFull(fft(iftshift(v, inplace=False))), inplace=False)
    vfr = real(vf)
    vfi = imag(vf)

    rr = vol(vfr)
    ii = vol(vfi)
    rotateSpline(vfr, rr, phi, psi, the)
    rotateSpline(vfi, ii, phi, psi, the)

    # print vfr(12,12,12),rr(12,12,12)
    vv = mergeRealImag(rr, ii)

    return ftshift(ifft(fullToReduced(iftshift(vv, inplace=False))), inplace=False) / v.numelem()

vv = fourier_rotate(v, phi, psi, the)
vv.write('v2.em')

from pytom.basic.transformations import rotateFourierSpline
vvv = rotateFourierSpline(v,phi, psi, the)
vvv.write('v3.em')