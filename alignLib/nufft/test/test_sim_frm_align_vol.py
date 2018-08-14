from pytom.tools.files import simulationDescriptionToParticleList
pl = simulationDescriptionToParticleList('/fs/pool/pool-foerster/data/thomas/simulations/model1/SNR1','/fs/pool/pool-foerster/data/thomas/simulations/model1/SNR1/')
pl = pl[0:100] # only the first 100

# this is for construct the template
# pl2 = pl[0:100]
# pl2.average('SNR0.01_first100.em',True)

from pytom_volume import read

r = read('/fs/home/ychen/data/alignment/simulation/SNR1_first50.em')

from frm import frm_align_vol

from pytom.tools.maths import rotation_distance, euclidianDistance

from pytom.tools.timing import Timing

t = Timing()
t.start()

dis_offset = []
ang_offset = []

for pp in pl:
	v = read(pp.getFilename())
	pos, ang, score = frm_align_vol(v, [-60.0, 60.0], r, [8, 32], 10)
	g_pos = pp.getShift().toVector()
	g_pos = [g_pos[0]+50, g_pos[1]+50, g_pos[2]+50]
	g_ang = [pp.getRotation().getZ1(), pp.getRotation().getZ2(), pp.getRotation().getX()]

	dis_offset.append(euclidianDistance(g_pos, pos))
	ang_offset.append(rotation_distance(g_ang, ang))
	print euclidianDistance(g_pos, pos), rotation_distance(g_ang, ang)

tt = t.end()

import numpy as np
print tt/100, np.mean(dis_offset), np.mean(ang_offset)