# compare the adaptive approach with Fourier spline interploation and NFFT.

from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import timing
from pytom.basic.structures import WedgeInfo
from nufft import fourier_rotate_vol


# v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
v = read('/fs/home/ychen/matlab/template/binning/tmp.em')
v2 = vol(v)

wedge = WedgeInfo(30.0)

diff_old = []
diff_new = []
total_time1 = 0.0
total_time2 = 0.0

for i in xrange(100):
    phi = np.random.randint(360)
    psi = np.random.randint(360)
    the = np.random.randint(180)
    
    # rotateSpline(v, v2, phi, psi, the)
    v2 = fourier_rotate_vol(v, [phi, psi, the])
    v2 = wedge.apply(v2)
    
    t = timing()

    # Fourier spline method
    t.start()
    res = frm_fourier_adaptive_wedge_vol(v2, [-60, 60], v, [-90, 90], [4, 32], v.sizeX()/2-3)
    ang = frm_find_best_angle(res, 32)
    t1 = t.end()

    dist_old = rotation_distance([phi, psi, the], ang)
    diff_old.append(dist_old)
    total_time1 += t1
    
    # NUFFT method
    t.start()
    # res = frm_nufft_adaptive_wedge_vol(v2, [-60, 60], v, [-90, 90], [4, 32], v.sizeX()/2-3)
    # ang2 = frm_find_best_angle(res, 32)
    pos, ang2, peak_value = frm_match(v2, [-60, 60], v, [-90, 90], [4, 32], v.sizeX()/2-3)
    t2 = t.end()
    
    dist_new = rotation_distance([phi, psi, the], ang2)
    diff_new.append(dist_new)
    total_time2 += t2

    print dist_old, dist_new
    
print
print np.mean(diff_old)
print np.mean(diff_new)
print total_time1/100, total_time2/100