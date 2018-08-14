"""
Compare the computational speed of SOFT and FRM.
"""

import numpy as np
from sh.soft import *
from sh.frm import *
from pytom.tools.maths import rotation_distance
from pytom_volume import *
from sh.vol2sf import vol2sf
from pytom.tools.timing import timing

b = 64

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
v2 = vol(v)
r = 8


f = vol2sf(v, r, b)
rotateSpline(v, v2, 30, 30, 30)
g = vol2sf(v2, r, b)

t = timing()

t.start()
for i in xrange(1000):
	res = soft_corr(g, f)

print t.end()

t.start()
for i in xrange(1000):
	res = frm_corr(g, f)

print t.end()