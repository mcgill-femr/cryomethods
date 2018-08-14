# search the position and the orientation

from pytom_volume import *
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


# v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/binning/tmp.em')
v = read('/fs/home/ychen/matlab/fromPDB/80SRibosome.em')

wedge = WedgeInfo(30.0)

diff_old = []
# diff_new = []
total_time1 = 0.0
# total_time2 = 0.0

for i in xrange(10):
    phi = np.random.randint(360)
    psi = np.random.randint(360)
    the = np.random.randint(180)
    offset = 0 #1
    shiftx = 0 #np.random.randint(-offset, offset)
    shifty = 0 #np.random.randint(-offset, offset)
    shiftz = 0 #np.random.randint(-offset, offset)
    
    # shift
    # v2 = shift(v, shiftx, shifty, shiftz, 'spline')

    # rotate
    v2 = fourier_rotate_vol(v, [phi, psi, the])

    # add some noise
    # v2 = add(v2, 0.01)

    # finally apply the wedge
    v2 = wedge.apply(v2)
    
    t = Timing()

    # frm_match
    t.start()
    pos, ang, peak_value = frm_match(v2, [-60, 60], v, [-90, 90], [4, 32], v.sizeX()/2-3, offset)
    t1 = t.end()

    dist_old = rotation_distance([phi, psi, the], ang)
    diff_old.append(dist_old)
    total_time1 += t1

    print [shiftx, shifty, shiftz], pos, dist_old
    
print
print np.mean(diff_old)
# print np.mean(diff_new)
print total_time1/100#, total_time2/100