from pytom_volume import *
from pytom_numpy import *
import numpy as np

v = np.ones(shape=(10,20,30), dtype='float32', order='F')
v[1,2,3]=100
print v.strides

vv = npy2vol(v, 3)
vv.info('')
print vv(1,1,1)
print vv(1,2,3)