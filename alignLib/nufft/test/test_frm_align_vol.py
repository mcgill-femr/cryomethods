from pytom_volume import *
from sh.frm import *
from sh.soft import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance, euclidianDistance
from pytom.tools.timing import Timing
from pytom.basic.structures import WedgeInfo
from nufft import fourier_rotate_vol
from pytom.basic.transformations import shift
from pytom.simulation.whiteNoise import add

v = read('/fs/home/ychen/matlab/fromPDB/80SRibosome.em')

wedge = WedgeInfo(30.0)

diff_old = []
total_time1 = 0.0

for i in xrange(100):
    phi = np.random.randint(360)
    psi = np.random.randint(360)
    the = np.random.randint(180)
    offset = 10
    shiftx = np.random.randint(-offset, offset)
    shifty = np.random.randint(-offset, offset)
    shiftz = np.random.randint(-offset, offset)

    # first rotate and then shift
    v2 = fourier_rotate_vol(v, [phi, psi, the])
    v2 = shift(v2, shiftx, shifty, shiftz, 'spline')

    # add some noise
    v2 = add(v2, 0.01)

    # finally apply the wedge
    v2 = wedge.apply(v2)
    
    t = Timing()

    # frm_match
    t.start()
    pos, ang = frm_align_vol(v2, [-60, 60], v, [8, 32], 10)
    t1 = t.end()

    dist_old = rotation_distance([phi, psi, the], ang)
    diff_old.append(dist_old)
    total_time1 += t1

    print euclidianDistance([shiftx+v.sizeX()/2, shifty+v.sizeY()/2, shiftz+v.sizeZ()/2], pos), dist_old
    
print
print np.mean(diff_old)
print total_time1/100