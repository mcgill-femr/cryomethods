# import numpy as np
# a = np.random.randn(3, 3)
# a[1][1] = a.max()+1 # set the max in the center

# dx = (a[2][1] - a[0][1])/2
# dy = (a[1][2] - a[1][0])/2
# dxx = a[2][1] + a[0][1] - 2*a[1][1]
# dyy = a[1][2] + a[1][0] - 2*a[1][1]
# dxy = (a[2][2] - a[2][0] - a[0][2] + a[0][0])/4
# det = 1/(dxx*dyy - dxy*dxy)

# deltax = -(dyy*dx - dxy*dy) * det
# deltay = -(dxx*dy - dxy*dx) * det
# print deltax, deltay

# ix = 1 + deltax
# iy = 1 + deltay

# peak = a[1][1] + dx*deltax + dy*deltay + deltax**2*dxx/2 + deltax*deltay*dxy + deltay**2*dyy/2

# print a
# print ix, iy, peak

# c = np.array([[dxx, dxy], [dxy, dyy]])
# d = np.array([-dx, -dy])
# deltax, deltay = np.linalg.solve(c, d)
# print deltax, deltay

from pytom_volume import read
from pytom.basic.transformations import shift
from nufft import fourier_rotate_vol
from sh.frm import rt2tr

v = read('/fs/home/ychen/matlab/template/binning/tmp.em')
angle = [30,40,50]
trans = [3,-3,3]

# first shift, then rotate
v2 = shift(v, trans[0], trans[1], trans[2], 'spline')
v2 = fourier_rotate_vol(v2, angle)
v2.write('2.em')

angle, trans = rt2tr(trans, angle)

# first rotate, then shift
v2 = fourier_rotate_vol(v, angle)
v2 = shift(v2, trans[0], trans[1], trans[2], 'spline')
v2.write('1.em')
