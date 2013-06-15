#! /usr/bin/env python

import sys, os
from osgeo import gdal, gdal_array

#
# Coordinates (north, south, east, west)
# 
class Coords:
    north = 0
    south = 0
    east = 0
    west = 0


#
# input:
#   filename ==> HDF file
#   prod ==> product (such as chlor_a)
# outout: 2D array of product data
# 
def read_hdf_prod(filename, prod):
    
    dataset = gdal.Open(filename)
    
    #keep working on this--multiple products
    sub_dataset = dataset.GetSubDatasets()
    if len(sub_dataset) > 0:
        sub_headings = [x[1] for x in sub_dataset]
        chlor_index = next(idx for idx,string in enumerate(sub_headings) if prod in string)
        arr = gdal_array.LoadFile(sub_dataset[chlor_index][0])
        return arr
    else:
        try: 
            return gdal_array.DatasetReadAsArray(dataset)
        except: 
            print 'ERROR: can\'t process'
            sys.exit()
            
            
#
# input:
#   file ==> smi file
# output: extracted Map Projection (such as 'Equidistant Cylindrical')
# 
def get_smi_projection(file):
    dump = os.popen('gdalinfo ' + file).read().split('\n')

    try:
        idx1 = next(idx for idx,string in enumerate(dump) if 'Map Projection' in string)
        idx2 = dump[idx1].index('=') + 1
        val = dump[idx1][idx2:]
    except:
        val = 'none'
    
    return val
    

#
# input:
#   file ==> HDF file
# output: object of type Coords() with latitude and longitude from HDF file
#
def get_hdf_latlon(file):
    
    try:
        dump = os.popen('gdalinfo ' + file).read().split('\n')
        latlon_keys = ['Southernmost Latitude', 'Westernmost Longitude', 'Northernmost Latitude', 'Easternmost Longitude']   
        latlon = []
        extracted_coords = Coords()
    
        for key in latlon_keys:
            list_idx = next(idx for idx, string in enumerate(dump) if key in string)
            string_idx = dump[list_idx].index('=') + 1
            latlon.append(dump[list_idx][string_idx:])
    except:
        latlon = [0,0,0,0]
                
    extracted_coords.south = float(latlon[0])
    extracted_coords.west = float(latlon[1])
    extracted_coords.north = float(latlon[2])
    extracted_coords.east = float(latlon[3])

    return extracted_coords
    
    
#
# input:
#   file ==> level 2 HDF file
# output: array of products that can be mapped e.g. ['chlor_a', 'cdom_index', ...]
#
def get_l2hdf_prod(file):
    master_prod_list = ['angstrom','aot_862','aot_865','aot_869','cdom_index','chlor_a','ipar','Kd_490','nflh','par','pic','poc',
                        'Rrs_410','Rrs_412','Rrs_413','Rrs_443','Rrs_486','Rrs_488','Rrs_490','Rrs_510','Rrs_531','Rrs_547','Rrs_551',
                        'Rrs_555','Rrs_560','Rrs_620','Rrs_665','Rrs_667','Rrs_670','Rrs_671','Rrs_681','Rrs_645','Rrs_859','adg_giop',
                        'adg_gsm','adg_qaa','aph_giop','aph_gsm','aph_qaa','arp','a_giop','a_gsm','a_qaa','bbp_giop','bbp_gsm','bbp_qaa',
                        'bb_giop','bb_gsm','bb_qaa','BT','calcite_2b','calcite_3b','cfe','chlor_oc2','chlor_oc3','chlor_oc4','chl_clark',
                        'chl_gsm','chl_octsc','evi','flh','ipar','Kd_lee','Kd_morel','Kd_mueller','Kd_obpg','KPAR_lee','KPAR_morel','ndvi',
                        'poc_clark','poc_stramski_490','tsm_clark','Zeu_morel','Zhl_morel','Zphotic_lee','Zsd_morel', 'chl_oc2']
                        
    hdf_prod_list = []
    
    sub_dataset = gdal.Open(file).GetSubDatasets()
    
    # make a list of hdf dataset names available
    dataset_names = [x[1] for x in sub_dataset]
    first_idx = [i.index(']')+1 for i in dataset_names]
    last_idx = [i.index('(') for i in dataset_names]
    dataset_names = map(lambda i,j,k: i[j:k], dataset_names, first_idx, last_idx)
    dataset_names = map(lambda i: i.strip(), dataset_names)
    
    for each in dataset_names:
        if any([each in s for s in master_prod_list]):
            hdf_prod_list.append(each)
    
    return hdf_prod_list
    
    
#    
# input:
#   sensor_id ==> single character, beginning of satellite name, e.g. 'A', 'M', ...
#   prod_type ==> products ('color' or 'sst')
# output: comma-separated string of flags ('ATMFAIL,LAND,HILT,HISATZEN,STRAYLIGHT,CLDICE,...')
#
def get_sds7_default_l2flags(sensor_id, prod_type):
    sensor_subdir= ['czcs', 'hmodisa', 'hmodist', 'meris', 'modis', 'modisa', 'modist', 'ocrvc', 'seawifs', 'viirsn']
    
    if sensor_id == 'S' and prod_type == 'color':
         fname = '$OCSSWROOT/run/data/seawifs/l2bin_defaults.par'
    if sensor_id == 'A' and prod_type == 'color':
         fname = '$OCSSWROOT/run/data/hmodisa/l2bin_defaults.par'
    if sensor_id == 'T' and prod_type == 'color':
         fname = '$OCSSWROOT/run/data/hmodist/l2bin_defaults.par'
    if sensor_id == 'M' and prod_type == 'color':
         fname = '$OCSSWROOT/run/data/meris/l2bin_defaults.par'
    if sensor_id == 'V' and prod_type == 'color':
         fname = '$OCSSWROOT/run/data/viirsn/l2bin_defaults.par'
    if sensor_id == 'C' and prod_type == 'color':
         fname = '$OCSSWROOT/run/data/czcs/l2bin_defaults.par'


    if sensor_id == 'A' and prod_type == 'sst':
         fname = '$OCSSWROOT/run/data/modisa/l2bin_defaults_SST.par'
    if sensor_id == 'T' and prod_type == 'sst':
         fname = '$OCSSWROOT/run/data/modist/l2bin_defaults_SST.par'

    if sensor_id == 'V' and prod_type == 'sst':
         fname = '$OCSSWROOT/run/data/modisa/l2bin_defaults_SST.par'  

    result = os.popen('more ' + fname + ' | grep  flaguse').read()

    flags = result.split('=')

    if prod_type == 'sst': flags = [i + ',CLDICE,NAVWARN,SEAICE,SSTWARN,SSTFAIL' for i in flags]
    
    return flags[1]
    

