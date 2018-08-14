from pytom_volume import *
from pytom.basic.transformations import rotateFourierSpline
from nufft import fourier_rotate_vol
from pytom.basic.correlation import FSC

v = read('/fs/home/ychen/matlab/fromPDB/80SRibosome.em')

n = 36
step = 360/n

# step = 33

vl = vol(v)
vc = vol(v)
vs = vol(v)
vf = vol(v)
vv = vol(v)

for i in xrange(n):
	print i
	vl2 = vol(vl)
	rotate(vl2, vl, step,0,0)
	vc2 = vol(vc)
	rotateCubic(vc2, vc, step,0,0)
	vs2 = vol(vs)
	rotateSpline(vs2, vs, step,0,0)
	vf = rotateFourierSpline(vf, step,0,0)
	vv = fourier_rotate_vol(vv, [step,0,0])

	# step = -step


vl.write('vl.em')
vc.write('vc.em')
vs.write('vs.em')
vf.write('vf.em')
vv.write('vv.em')

sl = FSC(v, vl, v.sizeX()/2)
sc = FSC(v, vc, v.sizeX()/2)
ss = FSC(v, vs, v.sizeX()/2)
sf = FSC(v, vf, v.sizeX()/2)
sv = FSC(v, vv, v.sizeX()/2)

print sl
print sc
print ss
print sf
print sv