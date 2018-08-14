"""
Compare the accuracy of conventional template matching with the FRM.
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
from sh.soft import *
from pytom.basic.correlation import nxcc

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/temp80SRibosome.em')
m = read('/fs/home/ychen/matlab/test_frm/mask_11.em')
angles = AngleListFromEM("")
angles.readRotationsFromEMFile("angles_12.85_7112.em")
# angles.readRotationsFromEMFile("angles_17.86_3040.em")

v2 = vol(v)

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
	
	# add some noise
	# v2 = add(v2, 0.01)
	
	# normalize the vol
	# mean0std1(v2)
	
	t = timing()

	# old method
	angles.reset()
	t.start()

	# res = extractPeaks(v2, v, angles, None, m, True, None, verboseMode=False)
	# pos = peak(res[0], m)
	# ang_idx = res[1].getV(pos[0], pos[1], pos[2])
	# ang = angles.getRotations()[int(ang_idx)]

	tmp = vol(v)
	peak = 0.0
	angle = angles.nextRotation()
	while angle != [None, None, None]:
		rotateSpline(v, tmp, angle[0], angle[1], angle[2])
		res = nxcc(v2, tmp, m)
		if res >= peak:
			peak = res
			ang = angle
		angle = angles.nextRotation()
	
	t1 = t.end()

	dist_old = rotation_distance([phi, psi, the], ang)
	diff_old.append(dist_old)
	total_time1 += t1
	
	# new method
	t.start()
	ang2 = frm_get_best_angle(v2, v, 32, None, False)
	t2 = t.end()

	dist_new = rotation_distance([phi, psi, the], ang2)
	diff_new.append(dist_new)
	total_time2 += t2

	print dist_old, dist_new
	
print diff_old
print diff_new
print total_time1/100, total_time2/100
