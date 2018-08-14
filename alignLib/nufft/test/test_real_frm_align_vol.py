from pytom_volume import read
from sh.frm import frm_align_vol
from pytom.tools.maths import rotation_distance, euclidianDistance
from pytom.tools.timing import Timing
from pytom.basic.structures import ParticleList
from pytom.basic.structures import Shift, Rotation

pl = ParticleList('.')
pl.fromXMLFile('/fs/home/ychen/4Chen/first100.xml')

r = read('/fs/home/ychen/4Chen/avg_first100.em')

for pp in pl:
	v = read(pp.getFilename())
	pos, ang = frm_align_vol(v, [-60.0, 60.0], r, [8, 32], 10, mask=30)
	pp.setShift(Shift([pos[0]-v.sizeX()/2, pos[1]-v.sizeY()/2, pos[2]-v.sizeZ()/2]))
	pp.setRotation(Rotation(ang))

pl.average('average.em', True)