"""
Test the effect of normalization. OBSOLETE!!! Since the normalization problem is already solved mathematically. Oh, yeah~~~
"""

from sh.frm import *
from pytom.localization.extractPeaks import extractPeaks
from pytom_volume import *
from pytom.angles.fromFile import AngleListFromEM
from pytom.basic.structures import Rotation
from pytom.basic.normalise import mean0std1
import numpy as np
from pytom.simulation.whiteNoise import add
from pytom.tools.maths import rotation_distance
from pytom.tools.timing import timing

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')

v2 = vol(v)

diff_old = []
diff_new = []

# mean0std1(v)
for i in xrange(100):
	phi = np.random.randint(360)
	psi = np.random.randint(360)
	the = np.random.randint(180)
	rotateSpline(v, v2, phi, psi, the)
	
	# add some noise
	# v2 = add(v2, 0.01)
	
	# normalize the vol
	# mean0std1(v2)

	# old method
	ang = frm_get_best_angle(v, v2, 32, None, norm=True)

	dist_old = rotation_distance([phi, psi, the], ang)
	diff_old.append(dist_old)
	
	# new method
	ang2 = frm_get_best_angle(v, v2, 32, None, norm=False)

	dist_new = rotation_distance([phi, psi, the], ang2)
	diff_new.append(dist_new)

	print dist_old, dist_new
