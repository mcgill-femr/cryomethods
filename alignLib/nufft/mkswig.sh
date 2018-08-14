#!/bin/sh

swig -python nufft.i
gcc -fPIC -O3 -c nufft.c nufft_wrap.c -I/usr/include/python2.6 -I/usr/lib/python2.6/dist-packages/numpy/core/include -I/fs/home/ychen/include
ld -shared nufft.o nufft_wrap.o -L/fs/home/ychen/lib -lfftw -lm -L/fs/home/ychen/lib/ -lnfft3 -o _swig_nufft.so
