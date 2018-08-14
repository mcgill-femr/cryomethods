# search the position and the orientation

from pytom_volume import read, vol, rotateSpline
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import Timing
from pytom.basic.structures import WedgeInfo
from nufft import fourier_rotate_vol
from pytom.basic.transformations import shift
from pytom.simulation.whiteNoise import add


# v = read('/fs/home/ychen/matlab/template/binning/tmp.em')
v = read('/fs/home/ychen/matlab/fromPDB/80SRibosome.em')

v2 = vol(v)
wedge = WedgeInfo(30.0)

diff_old = []
diff_new = []
total_time1 = 0.0
total_time2 = 0.0

for i in xrange(5):
    phi = np.random.randint(360)
    psi = np.random.randint(360)
    the = np.random.randint(180)
    offset = 15
    shiftx = np.random.randn()*offset
    shifty = np.random.randn()*offset
    shiftz = np.random.randn()*offset
    
    # test only rotate
    # rotateSpline(v, v2, phi, psi, the)

    # both shift and rotate
    v2 = shift(v, shiftx, shifty, shiftz, 'spline')
    v2 = fourier_rotate_vol(v2, [phi, psi, the])

    # add some noise
    v2 = add(v2, 0.01)

    # finally apply the wedge
    v2 = wedge.apply(v2)
    
    t = Timing()

    t.start()
    ang = frm_determine_orientation(v2, [-60, 60], v, [-90, 90], [4, 32], 30)#v.sizeX()/2-3)
    t1 = t.end()

    dist_old = rotation_distance([phi, psi, the], ang)
    diff_old.append(dist_old)
    total_time1 += t1

    # 2nd method
    t.start()
    res = frm_fourier_adaptive_wedge_vol(v2, [-60, 60], v, [-90, 90], [4, 32], 30)#v.sizeX()/2-3)
    ang2, peak = frm_find_best_angle_interp(res, 32)
    t2 = t.end()

    dist_new = rotation_distance([phi, psi, the], ang2)
    diff_new.append(dist_new)
    total_time2 += t2

    print [shiftx, shifty, shiftz], dist_old, dist_new
    
print
print np.mean(diff_old)
print np.mean(diff_new)
print total_time1/100, total_time2/100