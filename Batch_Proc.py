#! /usr/bin/env python

import sys
sys.path.insert(0, 'utilities')

import batch_L12
import batch_L23

sys.dont_write_bytecode = True



##########################################################
# To execute, edit the directories and variables below,
# and call from the command line by typing:
#          $ python Batch_Proc.py
##########################################################
##########################################################

# Level of input data: '1' for 1a
Input_Level ='3'
# Level of final processing desired
# Specify '2' for Level-2 and '3' for Level-3 binned and mapped
Final_level = '3'

# Note: Modis High Resolution products can only be processed to Level-2

######  Setup the input and output directories ###########

# Location of the Level-1 Files:
l1a_dir = '/Users/satellite/data/aqua_l1a_small_batch'
# Location where the Level-2 Files will be written:
l2_dir = '/Users/satellite/data/Level_2'
# Location where L3binmap Files and PNGs will be written:
binmap_dir = '/Users/satellite/Desktop/L3_binmap'

# If Level-2 and Level-3 directories are not specified, they
# will be created as 'L2_files' and 'L3_binmap' in the same directory
# as your Level-1 directory

######  Additional Variables ######
# All of the following variables are optional

# The products that you would like to be processed from L1 to L3
prod_list = 'OC_suite' #Defaults will be the OC_suite

# Latitude and Longitude for spatial binning and PNGs
latlon = '40,-72,46,-66'   #S,W,N,E #Default will be pulled from L2 metadata

# Spatial Resolution for binning and PNGs
space_res = '9' #Default is 9km, options are 1,2,4,9,36

# Temporal binning - Daily, Weekly, or Monthly
time_period = 'DLY' #Default is DLY, options are DLY, WKY, or MON

# High Resolution processing for Modis
hires = 'off' #Default is off, options are on, off

# Projection for standard mapped image
smi_proj = 'RECT' #Default is RECT, options are RECT for rectangular, or SIN for sinusoidal

# Flags to be used for color products
color_flags = 'standard' #Default is standard, as set by SeaDAS

# Flags to be used for sst products
sst_flags = 'standard' #Default is standard, as set by SeaDAS

# Statistics, on or off
stats_yesno = 'no' #Default is no, options are yes, no

# Nitrogen Dioxide
NO2_onoff = 'off' #Default is off, options are on, off

# Use of Short Wave Infrared
swir_onoff = 'off' #Default is off, options are on, off

##########################################################
##########################################################
##########################################################
##########################################################
##########################################################
##########################################################

if Input_Level == '1' and Final_level == '3':
    batch_L12.batch_proc_L12(l1a_dir, l2_dir, prod_list, NO2_onoff, swir_onoff, hires)
    batch_L23.batch_proc_L23(l2_dir, binmap_dir, prod_list, space_res,time_period, color_flags, sst_flags, latlon, smi_proj, stats_yesno)
elif Input_Level =='1' and Final_level == '2':
    batch_L12.batch_proc_L12(l1a_dir, l2_dir, prod_list, NO2_onoff, swir_onoff, hires)
elif Input_Level == '2' and Final_level == '3':
    batch_L23.batch_proc_L23(l2_dir, binmap_dir, prod_list, space_res,time_period, color_flags, sst_flags, latlon, smi_proj, stats_yesno)
else:
    print '#####  Please specify different input and output levels  #####'
    sys.exit()



