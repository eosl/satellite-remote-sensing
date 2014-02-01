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
def read_aviso_madt_nc(file, lat_north=90, lat_south=-90, lon_west=-180, lon_east=180):
    ssa = read_cdf_prod(file, 'Grid_0001')
    ssa = np.where(ssa > 10.0e10, np.nan, ssa)
    
    sla = ssa.T #transpose
    
    lat_values = read_cdf_prod(file, 'NbLatitudes') # -90 ... 90
    lon_values = read_cdf_prod(file, 'NbLongitudes') # 0 ... 360
    
    # put longitudes to correct values
    lon_values = np.where(lon_values <= 180, lon_values, lon_values - 360) # 0 ... 180, -180 ... 0

    # get resized image
    [mapped, pixels_per_lat, pixels_per_lon] = map_resize(sla, lat_values, lon_values, 1080, 540)
    
    # subscene using lat/lon
    mapped = mapped[(lat_south + 90)*pixels_per_lat : (lat_north + 90)*pixels_per_lat, (lon_west + 180)*pixels_per_lon : (lon_east + 180)*pixels_per_lon]
    
    
    return mapped