#! /usr/bin/env python

import os, sys
sys.dont_write_bytecode = True


import numpy as np
import zipfile, tarfile
import shutil
import hdf_utilities as hu



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
# puts old compressed files in separate directory
# input:
#   file ==> zipped file
#
def decompress_file(file):
    file_base = os.path.basename(file)
    path = os.path.dirname(file)
    new_dir = os.path.dirname(path) + '/compressed/'
    
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    if zipfile.is_zipfile(file):
        zip = zipfile.ZipFile(file)
        zip.extractall(path + '/')
        shutil.move(file, new_dir + file_base)
    elif tarfile.is_tarfile(file):
        tar = tarfile.open(file)
        tar.extractall(path + '/')
        tar.close()
        shutil.move(file, new_dir + file_base)
    elif (file.find('.gz') != -1):
        os.system("gunzip " + file)
    else: 
        print "Wrong archive or filename"
    

#
# returns True is file is a zipped or tarred file
# else returns false
#        
def is_compressed(file):
    if zipfile.is_zipfile(file) or tarfile.is_tarfile(file) or (file.find('.gz') != -1):
        return True
    else: return False
    
    


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

    

#
# get rid of ~ at beginning and / at end of file name
#
def path_reformat(path):
    path = path.strip()

    # get rid of troublesome '/' at end
    if path[-1] == '/':
        path = path[:-1]

    # get complete path
    if path[0] == '~':
        path = os.path.expanduser(path)
        
    return path
  
  
    
#
# get user products that match the products in the HDF
# input: HDF file, list of products [prod1,prod2,...]
# output: list of matched products [prod1,prod2,...]
#
def get_product_list(file, products):   
    # Get color products from HDF and match them to input products
    color_prod = []
          
    #get all products available to HDF
    all_prod = np.asarray(hu.get_l2hdf_prod(file))

    if products[0] == 'all':
        color_prod = all_prod
    else:
        #for each user-specified product, put in color_prod if also availible to HDF file
        for pr in products:
            good_prod_indx = np.where( all_prod == pr )
            if len(good_prod_indx) != 0: 
                color_prod = np.concatenate((color_prod, all_prod[good_prod_indx]), axis=0)
            
    #get rid of any empty products
    color_prod = color_prod[np.where(color_prod != '')]

    return color_prod
    
    
    
    