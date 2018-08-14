from pytom_volume import *
from pytom.basic.fourier import fft, ifft, ftshift, iftshift

v = read('/fs/home/ychen/matlab/template/binning/temp80SRibosome_bin2.em')
# v = read('/fs/home/ychen/matlab/template/temp80SRibosome.em')

fv = fft(v)

r1 = real(fv)
i1 = imag(fv)


fv2 = fullToReduced(reducedToFull(fv))


r2 = real(fv2)
i2 = imag(fv2)

(r1-r2).info('')
(i1-i2).info('')


fv3 = fullToReduced(iftshift(ftshift(reducedToFull(fv), inplace=False), inplace=False))


r3 = real(fv3)
i3 = imag(fv3)

(r1-r3).info('')
(i1-i3).info('')