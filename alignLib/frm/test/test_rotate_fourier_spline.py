from pytom_volume import *
from pytom.basic.transformations import rotateFourierSpline, shift
from pytom.basic.correlation import FSC

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/temp80SRibosome.em')
# v = read('/fs/home/ychen/matlab/fromPDB/80SRibosome.em')

# n = 36
# step = 360/n

# vl = vol(v)
# vc = vol(v)
# vs = vol(v)
# vf = vol(v)

# for i in xrange(n):
#	print i
#	vl2 = vol(vl)
#	rotate(vl2, vl, step,0,0)
#	vc2 = vol(vc)
#	rotateCubic(vc2, vc, step,0,0)
#	vs2 = vol(vs)
#	rotateSpline(vs2, vs, step,0,0)
#	vf = rotateFourierSpline(vf, step,0,0)

# vl.write('vl.em')
# vc.write('vc.em')
# vs.write('vs.em')
# vf.write('vf.em')

# sl = FSC(v, vl, v.sizeX()/2)
# sc = FSC(v, vc, v.sizeX()/2)
# ss = FSC(v, vs, v.sizeX()/2)
# sf = FSC(v, vf, v.sizeX()/2)

# print sl
# print sc
# print ss
# print sf

res = shift(v, 15.3,15.3,15.3)
res.write('res.em')

#res = shift(v, 1.3,2.3,3.3,'spline')
#res.write('res2.em')