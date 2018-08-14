"""
The same with test_wedge_corr but using SOFT way.
"""

from pytom_volume import *
from sh.frm import *
from sh.vol2sf import vol2sf
import numpy as np
from pytom.tools.maths import rotation_distance
from sh.soft import *

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
r = 8
b = 32
start = -60
end = 60
wedge = create_wedge_sf(start, end, b)
# m1 = wedge+0.001
whole = np.ones(4*b**2)


sf = np.array(vol2sf(v, r, b))
sf = sf - np.min(sf) + 1. # set all values above 1
# sf = sf / m1

# sf = create_wedge_sf(start, end, b, 1, 10)

sf2 = sf * wedge

res = frm_corr(sf2, sf)
ang = frm_find_best_angle(res, b)
print ang, rotation_distance([0, 0, 0], ang)
# print res.max(), res[0][b][b]

res = frm_constrained_corr(sf2, wedge, sf, whole)
ang = frm_find_best_angle(res, b)
print ang, rotation_distance([0, 0, 0], ang)

# do it in soft way!
# res2 = soft_corr(sf, sf2)
res2 = soft_constrained_corr(sf2, wedge, sf, whole)
ang2 = soft_find_best_angle(res2, b)

print ang2, rotation_distance([0, 0, 0], ang2)
