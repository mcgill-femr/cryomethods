from sh.vol2sf import vol2sf
from pytom_volume import *
v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')

r = 8
b = 32

for i in xrange(1000):
	sf = vol2sf(v, r, b)