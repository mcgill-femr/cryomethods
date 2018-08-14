from pytom_volume import *
from pytom.basic.transformations import rotateFourierSpline
from nufft import fourier_rotate_vol, fourier_interpolate_3d_vol

# v = read('/fs/home/ychen/matlab/fromPDB/80SRibosome.em')
v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')

# v2 = vol(v)

# rotateSpline(v, v2, 0,0,0)
# v2.write('res.em')

# v2 = rotateFourierSpline(v, 0,0,0)
# v2.write('res2.em')

# v2 = fourier_rotate_vol(v, [0,0,0])
# v2.write('res3.em')

from pytom.basic.fourier import *
fv = fft(v)
fvv = ftshift(reducedToFull(fv), inplace=False)
# print fvv(1,2,3), fvv(12,12,12), fvv(23,22,21)
print fvv(12,12,12)

# res = fourier_interpolate_3d_vol(v, [[(1-12)/25.,(2-12)/25.,(3-12)/25.], [0.,0.,0.], [(23-12)/25.,(22-12)/25.,(21-12)/25.]])
res = fourier_interpolate_3d_vol(v, [0.,0.,0.])
print res

# from pytom.basic.fourier import *
# fv = fft(v)
# fvv = ftshift(reducedToFull(fv), inplace=False)
# print fvv(1,2,3), fvv(50,50,50)

# res = fourier_interpolate_3d_vol(v, [[(1-50)/100.,(2-50)/100.,(3-50)/100.], [0.,0.,0.]])
# print res