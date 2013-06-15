#! /usr/bin/env python

import os, sys
from numpy import *
from pylab import *
import shutil

sys.dont_write_bytecode = True



#
# input: 
#   ct ==> IDL color parameter file
# ouput: python color map
#
def custom_cmap(ct):
	f = open(ct)
	color_array = array([])
	for line in f.readlines():
		color_array = append(color_array, line)
	f.close()
	
	color_array = map( lambda i: map( lambda j: round(float(j)/255.0, 2), i.split() ), color_array[1:] )
	color_int_array = arange(0.0,1.0,round(1.0/(len(color_array)-1), 3))
	color_int_array[-2] = 1.0

	red_array = map( lambda i: i[0], color_array)
	green_array = map( lambda i: i[1], color_array)
	blue_array = map( lambda i: i[2], color_array)
	
	
	red_tup = [[color_int_array[i], red_array[i+1], red_array[i]] for i in range(0,len(color_int_array)-1)]
	green_tup = [[color_int_array[i], green_array[i+1], green_array[i]] for i in range(0,len(color_int_array)-1)]
	blue_tup = [[color_int_array[i], blue_array[i+1], blue_array[i]] for i in range(0,len(color_int_array)-1)]
	
	cdict = {'red': red_tup,		
			 'green': green_tup,	
			 'blue': blue_tup}
	
	return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,256)


#
# input: 
#   fname ==> text file with table of values (~/idl_pros/dly_wkl_mon_qcmasked_pros/png_min_max_settings/prod_min_max_tab_delimted_txt)
#   prod ==> product (such as chlor_a)
# 
# output: vector of values [product, minimum, maximum, scale type]
#
def get_prod_min_max(fname, prod):
    print '\ngetting product min/max for color scaling png output using:'
    print 'min/max table: ', fname
    print 'searching for product: ', prod
    
    f = open(fname)
    l = f.readlines()
    m = l[0].split('\r')
    try:
        ind = next(idx for idx, string in enumerate(m) if prod in string)
        a = m[ind].split('\t')
    except:
        a = []
    if len(a) == 0:
        print '#'*50
        print ' requested geophysical product not found in prod_min_max_table: '
        print ' table file ===> ', fname
        print ' to add a new product open max table and insert a new product line ===USING TABS TO SEPARATE COLUMN VALUES==='
        print ' new product to add ===> ', prod
        print '#'*50, '\n'
        return_vec = ['','','','']
    else:
        
        prod_vec =  a[0]
        minval_vec = a[1]
        maxval_vec = a[2]
        scaletype_vec = a[3]
        print 'getting min/max for =====> ', prod_vec, '\n\n'
        return_vec= [prod_vec, minval_vec, maxval_vec, scaletype_vec]

        
    return return_vec



#
# CREATES A PNG FILE
# 
# input:
#   png_fname ==> output png file
#   geophys_img ==> input 2D array of values
#   product ==> products (such as chlor_a)
#   latlon ==> object of type Coords()
#   proj_name ==> projection type (such as 'RECT' or 'CYL')
#
def write_smi_png(png_fname, geophys_img, product, latlon, proj_name):
    
    rootname = os.path.basename(png_fname)    
    #center_lat, center_lon = get_cntr_latlon(latlon)#not used
    rotation_deg = 0.0
    size_info = geophys_img.shape # returns (# rows, # cols)
    product = product.strip() #trim leading or trailing space
    
    global_smi_chk = '.main' in png_fname
    if global_smi_chk is True: center_lon = 0.0    
    if proj_name is 'Equidistant Cylindrical': proj_name = 'Cylindrical'
    
    #-------------------------------------------------------------------#
    prod_min_max_table = os.path.expanduser('dly_wkl_mon_qcmasked/png_min_max_settings/prod_min_max_tab_delimted_txt')
    prod_min_max_info = get_prod_min_max(prod_min_max_table, product)
    
    low_limit = prod_min_max_info[1]
    upper_limit = prod_min_max_info[2]
    scale_type = prod_min_max_info[3]
    
    if low_limit == '': low_limit = -999
    else: low_limit = float32(low_limit)
    if upper_limit == '': upper_limit = 999
    else: upper_limit = float32(upper_limit)
    if scale_type == '': scale_type = 'LIN'
    
    if scale_type == 'LOG':
        low_limit = log10(low_limit)
        upper_limit = log10(upper_limit)
        geophys_img = log10(geophys_img)

    if product[:3] != 'sst':
        cmap = custom_cmap(os.path.expanduser('dly_wkl_mon_qcmasked/color_tables/standard/02-standard_chl.lut'))
        color_bar_img_file= os.path.expanduser('dly_wkl_mon_qcmasked/color_bars/colorbar_seadas_std_chlor.png')   
    if product[:3] == 'sst':
        cmap = custom_cmap(os.path.expanduser('dly_wkl_mon_qcmasked/color_tables/standard/03-standard_sst.lut'))
        color_bar_img_file= os.path.expanduser('dly_wkl_mon_qcmasked/color_bars/colorbar_seadas_std_sst.png')

    
    #specify color map with NaN's as black
    cmap.set_bad('k')

    #save as png
    imsave(png_fname, geophys_img, cmap=cmap, vmin=low_limit, vmax=upper_limit)
    
    
    ##-------------- write png info file
    png_dir = os.path.dirname(png_fname)
    png_info = open(png_dir + '/README_SCALE', 'w')
    
    png_info.write('prod: ' + product)
    if scale_type == 'LIN': 
        png_info.write('\nMIN: ' + str(low_limit))
        png_info.write('\nMAX: ' + str(upper_limit))
    if scale_type == 'LOG':
        png_info.write('\nMIN: ' + str(10.0**low_limit))
        png_info.write('\nMAX: ' + str(10.0**upper_limit))
        
    png_info.write('\nSCALE: ' + scale_type)
    png_info.write('\nPROJECTION: ' + proj_name + '\n')
    png_info.write('\nLatitude - Longitude Limits...')
    png_info.write('\nnorth: ' + str(latlon.north))
    png_info.write('\nsouth: ' + str(latlon.south))
    png_info.write('\nwest: ' + str(latlon.west))
    png_info.write('\neast: ' + str(latlon.east) + '\n')
    png_info.write('\nA final note on scaling png files with this program.  You can use seadas interative display with the mapped.hdf files' +
                    'and play around with different scales min/max and log/lin to find the best settings for your product of' +
                    'interest and then you can go to the text file: ===> ' + prod_min_max_table + 
                    'and set up your own scale settings that are specific for your product OR for your specific geographic location or season.\n' +
                    '\nTo make add a new product to the current list of products to sceale, just append a line to the the prod_min_max_scales_tbl.txt file' +
                    'that looks idendical to the line above, then then change the product name to the scale info a appropriate for your product.\n' +
                    '\nNOTE:  Once a new scaling has been set, you must rerun the batch_cmd, but remember: YOU ONLY NEED TO' +
                    'RE-RUN THE DALY, WEEKLY, MONTHLY AVERAGE COMMMANDS AND NOT THE L1->L3 OR THE L2->L3 PROGRAMS.  This means that' + 
                    'making the scale corrections will be VERY FAST (as opposed to what will happen if you unnecessarily run the' +
                    'L1->L3 or L2->L3 processinng all over again - so comment out the L1-L3 or L2-L3 commands near the top of your batch_cmd file.')
    
    png_info.close()
    
    shutil.copyfile(color_bar_img_file, png_dir + os.path.basename(color_bar_img_file))


