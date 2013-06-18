#! /usr/bin/env python

import os, sys
import numpy as np
import zipfile, tarfile

sys.dont_write_bytecode = True

#
# input: 
#   latlon ==> object of type Coords()
# output: the center latitude and longitude
#  
def get_cntr_latlon(latlon):
    center_lat = 0.0
     
    if latlon.west > 0.0 and latlon.east > 180.0:
        center_lon = latlon.west + abs(latlon.east - latlon.west)/2.0
    elif latlon.west > 0.0 and latlon.east < 0.0:
        delta_w = 180.0 - abs(latlon.west)
        delta_e = 180.0 - abs(latlon.east)
        
        if delta_w > delta_e:
            center_lon = w + (delta_w + delta_e)/2.0
        else: center_lon = latlon.east - (delta_w + delta_e)/2.0
    else:
        center_lon = latlon.west + abs(latlon.west - latlon.east)

    
    return center_lat, center_lon
    

#
# input: 
#   file ==> data file with name including 'satID,year,jday,hour,min,sec', e.g. 'A2013125220000'
# output: integer julian day
#
def get_jday(file):
    file_base = os.path.basename(file)
    return int(file_base[5:8])
    


# 
# unzips and extracts tar and zip to same directory
# input:
#   file ==> zipped file
#
def decompress_file(file):
    new_file = os.path.basename(file)
    path = os.path.dirname(file) + '/'
    

    if zipfile.is_zipfile(file):
        zip = zipfile.ZipFile(file)
        zip.extractall(path)
    elif tarfile.is_tarfile(file):
        tar = tarfile.open(file)
        tar.extractall(path)
        tar.close()
    elif (file.find('.gz') != -1):
        os.system("gunzip " + file)
        output = path + file[:-3]
    else: 
        print "Wrong archive or filename"
    
         
    


# inputs: 
#   data ==> 2D array of values
#   latitudes ==> 1D array of latitudes
#   longitudes ==> 1D array of longitudes
#   xdim ==> number of x pixels in output image
#   ydim ==> number of y pixels in output image
# output: 2D array of size (xdim, ydim)
#
def map_resize(data, latitudes, longitudes, xdim, ydim):
    lon1 = -180.0
    lon2 = 180.0
    lat1 = -90.0
    lat2 = 90.0
    
    mapped = np.empty((ydim,xdim))
    mapped[:,:] = np.nan

    pixels_per_lat = ydim/(lat2 - lat1)
    pixels_per_lon = xdim/(lon2 - lon1)
    
    # map longitudes and latitudes to pixel number
    lon_pix = np.where(longitudes <= 180, (longitudes+180)*pixels_per_lon, (longitudes-179)*pixels_per_lon)
    lat_pix = map( lambda lat: (lat + 90)*pixels_per_lat, latitudes )

    # put each lat/lon in its spot on rectangular grid
    def func(lat,lon,value): mapped[lat,lon] = value    
    map( lambda i: map(lambda j: func(lat_pix[i], lon_pix[j], data[i,j]) ,range(0,len(lon_pix))) ,range(0,len(lat_pix)) )
    
    
    return mapped

    
    
    
    
    
    
