#! /usr/bin/env python

from numpy import *
from pylab import *
import sys, os
from subprocess import call
import glob
from osgeo import gdal
from osgeo import gdal_array
import shutil

sys.path.insert(0, 'utilities')
sys.dont_write_bytecode = True

from hdf_utilities import *
from general_utilities import *
from subprograms import *



# Coordinates (north, south, east, west)
class Coords:
    north = 0
    south = 0
    east = 0
    west = 0
    

    
#
# make bl2 files (l2bin)
#
def bl2_gen(filelist, l2bin_dir, product, named_flags_2check, space_res):
    print '\nloop >>>>>>----------->' + product
    print 'flags to check >>>>>>----------->' +  named_flags_2check + '\n'
    
    # take the first 14 characters of each file name and append bin suffix
    l2bin_filelist = [l2bin_dir + '/' + os.path.basename(i)[0:14] + '.bl2bin' for i in filelist]
    
    if not os.path.exists(l2bin_dir):
        os.makedirs(l2bin_dir)
    
    for j in range(0,len(filelist)):
    
        print '\n===============> running l2bin binary <==================\n'
        call(['l2bin', 
              'infile=' + filelist[j], 
              'ofile=' + l2bin_filelist[j], 
              'l3bprod=' + product, 
              'resolve=' + str(space_res).strip(),
              'flaguse=' + named_flags_2check])
    

#
# make ascii file of bl2 files
#
def ascii_gen(bl2dir, filelist):
    ascii_file_list = bl2dir + '/' + 'ascii_bl2_list.txt'

    f = open(ascii_file_list, 'w')
    for file in filelist:
        if os.path.exists(bl2dir + '/' + file + '.bl2bin'):
            f.write(bl2dir + '/' + file + '.bl2bin' + '\n')

    f.close()

    return ascii_file_list

#
# make bl3 files (l3bin)
# 
def bl3_gen(product, ascii_file_list, input_coords, bl3_fname):
    print '\n====> running l3bin binary for color <=======\n' 
    print 'ascii_list is : ', ascii_file_list
    
    if not os.path.exists(os.path.dirname(bl3_fname)):
        os.makedirs(os.path.dirname(bl3_fname))
    
    call(['l3bin', 
        'in=' + ascii_file_list,
        'out=' + bl3_fname,
        'out_parm=' + product,
        'latsouth=' + str(input_coords.south),
        'latnorth=' + str(input_coords.north),
        'lonwest=' + str(input_coords.west), 
        'loneast=' + str(input_coords.east), 
        'noext=' + '1'])
    
    os.remove(ascii_file_list)

#
# make mapped files (smigen)
#
def smi_gen(product, meas_names, meas_vec, bl3_fname, out_file, smi_proj, space_res, input_coords):
    print '\n====> running smigen binary for color <======='
    print 'stats = ', meas_names, '\n'  
    
    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))        
         
    call(['smigen',
          'ifile=' + bl3_fname,
          'ofile=' + out_file,
          'prod=' + product,
          'meas=' + meas_vec,
          'precision=' + 'F',
          'stype=' + '1',
          'projection=' + smi_proj,
          'resolution=' + space_res + 'km',
          'lonwest=' + str(input_coords.west).strip(),
          'loneast=' + str(input_coords.east).strip(),
          'latnorth=' + str(input_coords.north).strip(),
          'latsouth=' + str(input_coords.south).strip()])
    
    if os.path.exists(out_file):
        print '\nwrote file:', out_file
    else: print '\ncould not generate smi file!!!'


#
# creates png files from an smi file
#
def png_gen(smi_file, png_dir, product, meas_names):
    print '\n====> running write_smi_png for color <=======\n'
    
    prod_img = asarray(read_hdf_prod(smi_file, 'l3m_data'))
    bad_locations = where(asarray(prod_img) == -999)
    if bad_locations[0] is not -1:
        prod_img[bad_locations] = nan
    
    proj_name = get_smi_projection(smi_file)
    
    extracted_coords = get_hdf_latlon(smi_file)
    
    if not os.path.exists(png_dir):
        os.makedirs(png_dir)
    png_ofile = png_dir + '/' + os.path.basename(smi_file)[:-8] + '.png'
    
    # call to hdf png generating function
    write_smi_png(png_ofile, prod_img, product, extracted_coords, proj_name)
    
    if os.path.exists(png_ofile):
        print 'wrote file ', png_ofile, '\n\n'
    else: print 'could not generate png!!!'
    
 
    

#
# input: list of files [file1,file2,...], list of averages ['DLY','WKY','MON'] and an integer year
# output: [([start, end], [file1,file2,...]), ([start, end], [file1,file2,...]), ([start, end] ,[file1,file2,...]), ...]
#
def get_average(filelist, time_period, year):

    if time_period == 'DLY':
        start_day = arange(1,366)
        end_day = arange(1,366)
    elif time_period == 'WKY':
        start_day = arange(1,366,8)
        end_day = asarray(map(lambda i: i+7, start_day))
    elif time_period == 'MON':
        # check for leap years
        if (year - 1980)%4 != 0:
            start_day = array([1,32,60,91,121,152,182,213,244,274,305,335])
            end_day = array([31,59,90,120,151,181,212,243,273,304,334,365])
        else:
            start_day = array([1,32,61,92,122,153,183,214,245,275,306,336])
            end_day = array([31,60,91,121,152,182,213,244,274,305,335,366])
 
    grouping_list = [([],[]) for i in range(0,len(start_day))] #list of tuples
    
    for i in range(0,len(start_day)):
        grouping_list[i][0].append('%03d' % start_day[i])
        grouping_list[i][0].append('%03d' % end_day[i])
        
    # assign each file to a time group
    for file in filelist:

        for i in range(0,len(start_day)):

            if get_jday(file) >= start_day[i] and get_jday(file) <= end_day[i]:
                grouping_list[i][1].append(file)

    def f(x): return len(x[1])!=0
    grouping_list = filter(f, grouping_list) #cut empty groups
    
    
    return grouping_list
    
    
#
# check that preliminary conditions are met
# otherwise exit program
#
def preliminary_checks(length_filelist, length_uniq_syear, length_uniq_sat_type, smi_proj):
    # first check
    if length_filelist == 0:
    	print '\n########### PROGRAM batch_binmap.pro HALTED BECAUSE NO L2 FILES FOUND IN THE    #########'
    	print '########### SPECIFIED L2DIR. PLEASE GO BACK AND RECHECK THE DIRECTORY PATH THAT #########' 
    	print '########### WAS SPECIFIED IN THE BATCH_CMD_BINMAP FILE.                         #########\n'
        sys.exit()
        
    if length_uniq_syear > 1:
        print '##### PROGRAM HALTED BECAUSE L2DIR CONTAINS FILES FROM SEPARATE YEARS ####'
        print '##### PLEASE GO BACK AND PARSE L2 FILE INTO SEPARTE UNIQUE YEARS      ####'
        sys.exit()

    if length_uniq_sat_type > 1:
        print '##### PROGRAM HALTED BECAUSE L2DIR CONTAINS FILES FROM SEPARATE SENSORS        ####'
        print '##### PLEASE GO BACK AND PARSE L2 FILE INTO SEPARTE UNIQUE SENSOR DIRECTORIES  ####'
        
    if smi_proj != 'RECT' and smi_proj != 'SIN':
        print '##### PROGRAM HALTED BECAUSE SMI_PROJ WAS NOT SET TO EITHER: CYL OR SIN ####'
        print '##### PLEASE GO BACK AND CORRECT THE PROJECTION NAME...                  ####'
        sys.exit()


#
# get user products that match the products in the HDF
# input: HDF file, list of products [prod1,prod2,...]
# output: list of matched products [prod1,prod2,...]
#
def get_product_list(file, products):   
    # Get color products from HDF and match them to input products
    color_prod = []
          
    #get all products available to HDF
    all_prod = asarray(get_l2hdf_prod(file))

    if products[0] == 'all':
        color_prod = all_prod
    else:
        #for each user-specified product, put in color_prod if also availible to HDF file
        for pr in products:
            good_prod_indx = where( all_prod == pr )
            if len(good_prod_indx) != 0: 
                color_prod = concatenate((color_prod, all_prod[good_prod_indx]), axis=0)
            
    #get rid of any empty products
    color_prod = color_prod[where(color_prod != '')]

    return color_prod
    

#
# loop through and call each processing function (l2bin ==> make ascii ==> l3bin ==> smigen ==> png)
#
def process(filelist, time_period, out_dir, products, named_flags_2check, space_res, input_coords, chk, sat_type, year, stats_yesno, smi_proj):

    if time_period == 'DLY':
        ave_dir = 'daily'
    elif time_period == 'WKY':
        ave_dir = 'weekly'
    elif time_period == 'MON':
        ave_dir = 'monthly'


    # make directories
    temp = os.path.dirname(filelist[0])    
    l2bin_output = temp + '/l2bin'
    l3bin_output = temp + '/l3bin'


    if stats_yesno == 'yes':
        meas_vec = ['1', '2', '4']
        meas_names = ['mean', 'variance', 'npoints']
    else: 
        meas_vec = ['1']
        meas_names = ['mean']


    # returns groupings
    averages = get_average(filelist, time_period, int(year))

    # average 
    for file_group in averages: #file_group = ([start, end], [file1, file2, file3...])
        
        for prod in products:
        
            # make bl2 files
            bl2_gen(file_group[1], l2bin_output, prod, named_flags_2check, space_res)
        
            # make ascii file
            bl2_files = [os.path.basename(f)[:14] for f in file_group[1]]
            ascii_file_list = ascii_gen(l2bin_output, bl2_files)
   
            # make bl3 files--- one for each file_group
            l3bin_output_dir = l3bin_output + '/' + ave_dir
            l3bin_output_file = l3bin_output_dir + '/' + sat_type + str(year) + file_group[0][0] + str(year) + file_group[0][1] + '.bl3bin'
            bl3_gen(prod, ascii_file_list, input_coords, l3bin_output_file)
        
            # Now I have averaged files
            for s in range(0,len(meas_vec)):
    
                # make smigen files
                smi_output_dir = out_dir + '/' + ave_dir + '/' + prod + '/' + meas_names[s]
                smi_output_file = smi_output_dir + '/' + os.path.basename(l3bin_output_file)[:15]+'.'+prod+'-'+meas_names[s]+'.smi.hdf' 
                if os.path.exists(l3bin_output_file):
                    smi_gen(prod, meas_names[s], meas_vec[s], l3bin_output_file, smi_output_file, smi_proj, space_res, input_coords)
            
                # make png's
                if os.path.exists(smi_output_file):
                    png_gen(smi_output_file, smi_output_dir+'/png', prod, meas_names[s])
    
    shutil.rmtree(l2bin_output)
    shutil.rmtree(l3bin_output) 


 
        



#  
# setup environment variables
#
def setup(l2dir, smi_proj, latlon, stats_yesno, color_flags_to_check, sst_flags_to_check):
    filelist = asarray(glob.glob(l2dir + '/' + '*L2*'))
    
    # decompress files if necessary
    if any([is_compressed(fi) for fi in filelist]):
        for fi in filelist:
            decompress_file(fi)
        filelist = asarray(glob.glob(l2dir + '/' + '*L2*'))

    
    good_index = where( filelist != '' )  
       
    input_coords = Coords()
    if latlon[0] == 'whole':
        input_coords = get_hdf_latlon(glob.glob(l2dir + '/*')[0] )
    else:
        input_coords.north = latlon[2]
        input_coords.south = latlon[0]
        input_coords.east = latlon[3]
        input_coords.west = latlon[1] 
    
    if len(good_index[0]) != 0:
        filelist = filelist[good_index]
    
    filelist = list(set(sort(filelist))) # list of unique file names
    
    print '\nbatch process running...'
    print 'number of files found= ', len(filelist), '\n'
    
    
    root = [os.path.basename(name) for name in filelist]
    sat_type = [name[0] for name in root]
    syear = [name[1:5] for name in root]
    year = asarray(map(int, syear))[0] #I just defined 'year' as the first year in this list...
    
    # check if files are sst or oc
    sst_chk = ['SST' in name for name in root]
    color_chk = ['OC' in name for name in root]
    hires_chk = [('QKM' in name or 'HKM' in name) for name in root]
    
    uniq_syear = list(set(sort(syear))) #sorted list of unique years      
    uniq_sat_type = list(set(sort(sat_type))) #sorted list of unique satellites        
        
    # make sure things aren't too screwed up   
    preliminary_checks(len(filelist), len(uniq_syear), len(uniq_sat_type), smi_proj)
    

    # get flags to check
    color_named_flags_2check = ''
    sst_named_flags_2check = ''
    if color_flags_to_check == 'standard':
        color_named_flags_2check = get_sds7_default_l2flags(uniq_sat_type[0], 'color')
    if sst_flags_to_check == 'standard' and (uniq_sat_type[0]=='A' or uniq_sat_type[0]=='T' or uniq_sat_type[0]=='V'):
        sst_named_flags_2check = get_sds7_default_l2flags(uniq_sat_type[0], 'sst')


    return color_chk, sst_chk, hires_chk, color_named_flags_2check, sst_named_flags_2check, sat_type[0], filelist, input_coords, year

    
#
# process products and/or sst
#
def batch_proc_L23(l2dir, output_dir='not_specified', products=['all'], space_res='9', time_period=['DLY'], color_flags_to_check='standard', 
                    sst_flags_to_check='standard', latlon=['whole'], smi_proj='RECT', stats_yesno='no'):

    
    #no hi-res for now...
    hires = False
    
    # make sure directories are right (/ and ~)
    l2dir = l2dir.strip()
    output_dir = output_dir.strip()
    if l2dir[-1] == '/':
        l2dir = l2dir[:-1]
    if output_dir[-1] == '/':
        output_dir = output_dir[:-1]
    if l2dir[0] == '~':
        l2dir = os.path.expanduser(l2dir)
    if output_dir[0] == '~':
        output_dir = os.path.expanduser(output_dir)
        
    
    #setup variables
    color_chk, sst_chk, hires_chk, color_named_flags_2check, sst_named_flags_2check, sat_type, filelist, input_coords, year \
        = setup(l2dir, smi_proj, latlon, stats_yesno, color_flags_to_check, sst_flags_to_check)
        


    # put output data next to input data if not specified by user
    if output_dir == 'not_specified':
        output_dir = os.path.dirname(l2dir) + '/' + 'L3_binmap'

    
    # get rid of bad average value
    def f(x): return (x == 'DLY' or x == 'WKY' or x == 'MON')
    time_period = filter(f, time_period) #cut empty groups
    

    #---------------- setup products ---------------------#
    #OC
    color_file_indices = where( ((asarray(color_chk)==True) | (asarray(sat_type)=='M')) & (asarray(hires_chk)==hires) )
    color_files = list(asarray(filelist)[color_file_indices])
    
    # OC product list
    color_prod = get_product_list(color_files[0], products)
    
    #SST
    sst_file_indices = where( asarray(sst_chk)==True )[0]
    if len(sst_file_indices) != 0: sst_prod = ['sst']
    sst_files = list(asarray(filelist)[sst_file_indices])
    
    #-----------------------------------------------------#

    # for each average specified
    for average in time_period:        
        # process color products        
        if len(color_files) != 0:
            process(color_files, average, output_dir, color_prod, color_named_flags_2check, space_res, input_coords, 
                                                                            color_chk, sat_type, year, stats_yesno, smi_proj)
        
        # process sst
        if len(sst_files) != 0:
            process(filelist, average, output_dir, sst_prod, sst_named_flags_2check, space_res, input_coords, 
                                                                                sst_chk, sat_type, year, stats_yesno, smi_proj)


#
# defaults
#   
def main(*args):
    import getopt
    
    arg_options = ['l2_dir=', 'binmap_dir=','products=', 'space_res=', 'time_period=','color_flags=','sst_flags=','latlon=','smi_proj=','stats_yesno=']
    opts, arg = getopt.getopt(args, '', arg_options)

    if len(args) == 0:
        print '\nUsage:\n\t batch_L23.py --l2_dir=<l2_dir> --binmap_dir=<l2_dir> --products=<prod1,prod2,prod3,...> --space_res=<space_res> --time_period=<time_period> --color_flags=<flag1,flag2,...> --sst_flags=<flag1,flag2,...> --latlon=<S,W,N,E> --smi_proj=<smi_proj> --stats_yesno=<stats_yesno>\n\n'
        print '\t--'+arg_options[0][:-1]+' (required) ==> directory containing Level 2 data files'
        print '\t--'+arg_options[1][:-1]+' (optional, default=L3_binmap) ==> new directory that the l2bin and l3bin data files will be written to'
        print '\t--'+arg_options[2][:-1]+' (optional, defualt=all) ==> products contained in the L2 files to be mapped (chlor_a,poc,cdom_index,...)'
        print '\t--'+arg_options[3][:-1]+' (optional, default=9) ==> Spatial Resolution in km (1,4,9,36)'
        print '\t--'+arg_options[4][:-1]+' (optional, defualt=DLY) ==> Time period to be averages (DLY, WKY, MON)'
        print '\t--'+arg_options[5][:-1]+' (optional, defualt=standard) ==> Color flags to check'
        print '\t--'+arg_options[6][:-1]+' (optional, default=standard) ==> SST flags to check'
        print '\t--'+arg_options[7][:-1]+' (optional, default=whole) ==> Lat/LON --S,W,N,E. If not specified, finds latlon from HDF file'
        print '\t--'+arg_options[8][:-1]+' (optional, defualt=RECT) ==> SMI projection (RECT = rectangular, SIN = sinusoidal)'
        print '\t--'+arg_options[9][:-1]+' (optional, defualt=no) ==> Stats Yes/No'
    else:
        for option,value in opts:
            if option == '--' + arg_options[0][:-1]:
                arg1 = value
            if option == '--' + arg_options[1][:-1]:
                arg2 = value
            if option == '--' + arg_options[2][:-1]:
                arg3 = value
            if option == '--' + arg_options[3][:-1]:
                arg4 = value
            if option == '--' + arg_options[4][:-1]:
                arg5 = value
            if option == '--' + arg_options[5][:-1]:
                arg6 = value
            if option == '--' + arg_options[6][:-1]:
                arg7 = value
            if option == '--' + arg_options[7][:-1]:
                arg8 = value
            if option == '--' + arg_options[8][:-1]:
                arg9 = value
            if option == '--' + arg_options[9][:-1]:
                arg10 = value

        if 'arg2' not in locals():
            arg2 = 'not_specified'
        if 'arg3' not in locals():
            arg3 = 'all'
        if 'arg4' not in locals():
            arg4 = '9'
        if 'arg5' not in locals():
            arg5 = 'DLY'
        if 'arg6' not in locals():
            arg6 = 'standard'
        if 'arg7' not in locals():
            arg7 = 'standard'
        if 'arg8' not in locals():
            arg8 = 'whole'
        if 'arg9' not in locals():
            arg9 = 'RECT'
        if 'arg10' not in locals():
            arg10 = 'no'


        if 'arg3' in locals():
            arg3 = arg3.split(',') #split products into list (chlor_a,sst,...)
        if 'arg5' in locals():
            arg5 = arg5.split(',') #split averages into list (DLY,WKY,MON)
        if 'arg8' in locals():
            arg8 = arg8.split(',') #split latlon into list (south,west,north,east)

        batch_proc_L23(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10)
        
        
#
# COMMAND LINE CALL
#
if __name__=='__main__':
    
    main(*sys.argv[1:])
    
            