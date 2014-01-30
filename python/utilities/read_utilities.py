#! /usr/bin/env python

import sys
sys.dont_write_bytecode = True

import scipy.io
import numpy as np
import scipy.interpolate as si
from general_utilities import *




#
# input: 
#    file ==> .nc file
#    prod ==> product (such as chlor_a)
# output: array of product data
#
def read_cdf_prod(file, prod):
    f = scipy.io.netcdf_file(file, 'r')
    
    return f.variables[prod][:].copy()
    

#
# input: 
#   file ==> .nc file
# output: array of mapped data from .nc file
#
def read_aviso_madt_nc(file):
    ssa = read_cdf_prod(file, 'Grid_0001')
    ssa = np.where(ssa > 10.0e10, np.nan, ssa)
    
    sla = ssa.T #transpose
    
    lat_values = read_cdf_prod(file, 'NbLatitudes')
    lon_values = read_cdf_prod(file, 'NbLongitudes')
    
    mapped = map_resize(sla, lat_values, lon_values, 1080, 540)
    
    
    return mapped
    
    


    