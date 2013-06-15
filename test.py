#! /usr/local/bin/python

from pylab import *
import sys

sys.path.insert(0, 'python/utilities')
from read_utilities import *
from general_utilities import *

file1 = '/Users/nicknardelli/Desktop/1.nc'
file2 = '/Users/nicknardelli/Desktop/2.nc'
file3 = '/Users/nicknardelli/Desktop/3.nc'

x = read_aviso_madt_nc(file1)



cmap = get_cmap('spectral')
cmap.set_bad('k')


imshow(x[:][::-1], cmap=cmap)

show()
# import zipfile, tarfile, os
# 
# file1 = '/Users/nicknardelli/Desktop/untitled/2.tar.gz'
# file2 = '/Users/nicknardelli/Desktop/untitled/3.zip'
# file3 = '/Users/nicknardelli/Desktop/untitled/4.tar'
# file4 = '/Users/nicknardelli/Desktop/untitled/5.tar.bz2'
# 
# 
# decompress_file(file2)