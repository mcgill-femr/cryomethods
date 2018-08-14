#!/bin/sh

gcc test.c -I/fs/home/ychen/include -L/fs/home/ychen/lib/ -lnfft3 -std=c99 -o test
