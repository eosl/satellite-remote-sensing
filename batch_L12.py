#! /usr/bin/env python

import glob
import os
from subprocess import call
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, 'utilities')

#-------------------------------
#           MODIS
#-------------------------------
def modis_level12(file_name, root_name, prod_list, color_l2_file_fname, sst_l2_file_fname, gas_combo_id, aerosol_corr_type, hires):
    # (modis_atteph.py)
    print '\n >=====>  checking for presence of attitude and emphemerise files locally and retrieving from web if needed...'
    os.system('modis_atteph.py -v ' + file_name)
    
    #generate geolocation file (modis_GEO.py)
    print '\n >=====>  generating geolocation file from modis L1A standard resolution bands...'
    fname_geo = root_name[0:14] + '.GEO'
    fname_atteph_list = root_name + '.atteph'
    os.system('modis_GEO.py -v -o ' + fname_geo + ' ' + file_name + ' ' + 'par=' + fname_atteph_list)
    
    # generate L1B from L1A (modis_L1B.py)
    print '\n >=====>  generating Level-1B file from Level-1A file and Geolocation File...'
    if hires == 'off':
        fname_l1b = root_name[0:14] + '.L1B_LAC'
        os.system('modis_L1B.py -v -o ' + fname_l1b + ' ' + file_name + ' ' + fname_geo)
    elif hires == 'on':
        fname_l1b = root_name[0:14] + '.L1B_LAC'
        fname_l1b_hkm = root_name[0:14] + '.L1B_HKM'
        fname_l1b_qkm = root_name[0:14] + '.L1B_QKM'
        os.system('modis_L1B.py -v -o ' + fname_l1b + ' ' + file_name + ' ' + fname_geo + ' -k ' + fname_l1b_hkm + ' -q ' + fname_l1b_qkm)

    # get ancillary data (getanc.py)
    print '\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...'
    os.system('getanc.py -v ' + file_name)
    fname_ancil_list = root_name + '.anc'
    
    
    # call l2gen c-compiled function
    print '\n >=====>  generating level-2 data from level-1 data using l2gen...'
    call(['l2gen',
          'ifile=' + fname_l1b,
          'ofile1=' + color_l2_file_fname,
          'l2prod1=' + prod_list,
          'ofile2=' + sst_l2_file_fname,
          'l2prod2=' + 'sst',
          'geofile=' + fname_geo,
          'resolution=' + '1000',
          'par=' + fname_ancil_list,
          'gas_opt=' + gas_combo_id,
          'aer_opt=' + aerosol_corr_type])
    
    # if high-resolution is specified
    if hires == 'on':
        print '\n >=====>  generating hires level-2 data from level-1 data using l2gen...'
        call(['l2gen',
             'ifile=' + fname_l1b,
             'ofile1=' + color_l2_file_fname + '_HKM',
             'l2prod1=' + 'chl_oc2,l2_flags',
             'geofile=' + fname_geo,
             'resolution=' + '500',
             'par=' + fname_ancil_list,
             'gas_opt=' + gas_combo_id,
             'aer_opt=' + aerosol_corr_type,
             'ctl_pt_incr=' + '1'])
        call(['l2gen',
             'ifile=' + fname_l1b,
             'ofile1=' + color_l2_file_fname + '_QKM',
             'l2prod1=' + 'Rrs_645,Rrs_859,l2_flags',
             'geofile=' + fname_geo,
             'resolution=' + '250',
             'par=' + fname_ancil_list,
             'gas_opt=' + gas_combo_id,
             'aer_opt=' + aerosol_corr_type,
             'ctl_pt_incr=' + '1'])



#-------------------------------
#           seawifs/meris
#-------------------------------
def seawifs_meris_level12(file_name, root_name, prod_list, color_l2_file_fname, gas_combo_id):
    # get ancillary data (getanc.py)
    print '\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...'
    os.system('getanc.py -v ' + file_name)
    fname_ancil_list = root_name + '.anc'
    
    # call l2gen c-compiled function
    call(['l2gen',
          'ifile=' + file_name,
          'ofile=' + color_l2_file_fname,
          'l2prod1=' + prod_list,
          'par=' + fname_ancil_list,
          'gas_opt=' + gas_combo_id])


#-------------------------------
#           viirs
#-------------------------------
def viirs_level12(file_name, prod_list, color_l2_file_fname, sst_l2_file_fname, gas_combo_id):
    first_band_root = file_name.split('/')[-1] # last directory in path
    first_band = glob.glob(file_name + '/' + 'SVM01*')[0] # first band in series
    geolocation_file = glob.glob(file_name + '/' + 'GMTCO*')[0] # geolocation file
    
    #ancillary list
    os.system('getanc.py -v ' + first_band)
    fname_ancil_list = first_band.split('/')[-1] + '.anc'
    
    # call l2gen c-compiled function
    call(['l2gen',
          'ifile=' + first_band,
          'ofile1=' + color_l2_file_fname,
          'l2prod1=' + prod_list,
          'ofile2=' + sst_l2_file_fname,
          'l2prod2=' + 'sst',
          'geofile=' + geolocation_file,
          'resolution=' + '1000',
          'par=' + fname_ancil_list,
          'gas_opt=' + gas_combo_id])



#-------------------------------
#       batch processing
#-------------------------------
def batch_proc_L12(l1a_dir, l2_dir='not_specified', prod_list='OC_suite', NO2_onoff='off', swir_onoff='off', hires='off'):

    # make sure directories are right (/ and ~)
    l1a_dir = l1a_dir.strip()
    l2_dir = l2_dir.strip()
    if l1a_dir[-1] == '/':
        l1a_dir = l1a_dir[:-1]
    if l2_dir[-1] == '/':
        l2_dir = l2_dir[:-1]
    if l1a_dir[0] == '~':
        l1a_dir = os.path.expanduser(l1a_dir)
    if l2_dir[0] == '~':
        l2_dir = os.path.expanduser(l2_dir)
        
        

    fname_l1a = glob.glob(l1a_dir + '/' + '*L1A*') #list of all files in level 1 directory

    # if user doesn't specify level 2 directory, make one next to L1 data directory
    if l2_dir == 'not_specified':
        l2_dir = os.path.dirname(l1a_dir) + '/' + 'L2_files'

    #make L2 directory
    if not os.path.exists(l2_dir):
        os.makedirs(l2_dir)

    root_name = [os.path.basename(i) for i in fname_l1a] #list of file names split from path
    root_name_trim = [name[0:14] for name in root_name] #list of file names without extension
    
    # LEVEL 2
    color_l2_file_fname = [l2_dir + '/' + name + '.L2_OC' for name in root_name_trim] #list of level 2 OC files to be created
    sst_l2_file_fname = [l2_dir + '/' + name + '.L2_SST' for name in root_name_trim] #list of level 2 SST files to be created
    
    # set NO2
    if NO2_onoff == 'on':
        gas_combo_id = '5'
    else:
        gas_combo_id = '1'

    # set SWIR
    if swir_onoff == 'on':
        aerosol_corr_type = '-9'
    else:
        aerosol_corr_type = '-3'

	# identify satellite by first letter in file name
    sat_id = root_name[0][0]
    print sat_id
    if (sat_id == 'A' or sat_id == 'T'):
        satellite_name = 'modis'
        if prod_list == 'OC_suite':
            prod_list = 'aot_869,angstrom,Rrs_412,Rrs_443,Rrs_488,Rrs_531,Rrs_547,Rrs_667,chlor_a,Kd_490,pic,poc,cdom_index,ipar,nflh'
    elif sat_id == 'S':
        satellite_name = 'seawifs'
        if prod_list == 'OC_suite':
            prod_list = 'aot_865,angstrom,Rrs_412,Rrs_443,Rrs_490,Rrs_510,Rrs_555,Rrs_670,chlor_a,Kd_490,pic,poc,cdom_index,par'
    elif sat_id == 'M':
        satellite_name = 'meris'
        if prod_list == 'OC_suite':
            prod_list = 'aot_865,angstrom,Rrs_413,Rrs_443,Rrs_490,Rrs_510,Rrs_560,Rrs_620,Rrs_665,Rrs_681,chlor_a,Kd_490'
    elif sat_id == 'V':
        satellite_name = 'viirs'
        if prod_list == 'OC_suite':
            prod_list = 'chlor_a,Kd_490,aot_862,angstrom,Rrs_410,Rrs_443,Rrs_486,Rrs_551,Rrs_671,pic,poc,par'


    # MODIS
    if 'modis' in satellite_name:
        for i in range(0,len(fname_l1a)):
            modis_level12(fname_l1a[i], root_name[i], prod_list, color_l2_file_fname[i], sst_l2_file_fname[i], gas_combo_id, aerosol_corr_type, hires)

    # SEAWIFS or MERIS RR
    if ('seawifs' in satellite_name or 'meris' in satellite_name):
        for i in range(0,len(fname_l1a)):
            seawifs_meris_level12(fname_l1a[i], root_name[i], prod_list, color_l2_file_fname[i], gas_combo_id)

    # VIIRS RR 
    if 'viirs' in satellite_name:
        for i in range(0,len(fname_l1a)):
            viirs_level12(fname_l1a[i], prod_list, color_l2_file_fname[i], sst_l2_file_fname[i], gas_combo_id)


    # clean up... 
    types = ['*.GEO','*.anc','*.atteph','*L1B_LAC','*L1B_HKM*','*L1B_QKM*','*.pcf']
    for t in types:
        for i in glob.glob(l1a_dir + '/' + t): os.remove(i)
        for i in glob.glob(t): os.remove(i)



#
# defaults
#
def main(*args):
    import getopt
    
    arg_options = ['l1a_dir=', 'l2_dir=','prod_list=', 'NO2_onoff=', 'swir_onoff=', 'hires=']
    opts, arg = getopt.getopt(args, '', arg_options)

    if len(args) == 0:
        print '\nUsage:\n\t batch_L12.py --l1a_dir=<l1a_dir> --l2_dir=<l2_dir> --prod_list=<prod1,prod2,prod2,...> --NO2_onoff<NO2_onoff> --swir_onoff=<swir_onoff>  --hires=<on/off>\n\n'
        print '\t--'+arg_options[0][:-1]+' (required) ==> directory containing Level 1 data files'
        print '\t--'+arg_options[1][:-1]+' (optional, default=L2_files) ==> new directory that Level 2 data files will be written to'
        print '\t--'+arg_options[2][:-1]+' (optional, default = OC_suite) ==> products to be extracted (chlor_a, poc, cdom_index,...)'
        print '\t\t-'+'OC_suite defaults contain Kd_490, Rrs_vvv, angstrom, cdom_index, chlor_a, par, pic, and poc'
        print '\t--'+arg_options[3][:-1]+' (optional, default=off) ==> Nitrogen Dioxide transmittance bitmask selector (on/off)'
        print '\t--'+arg_options[4][:-1]+' (optional, defualt=off) ==> aerosol mode option (on/off)'
        print '\t--'+arg_options[5][:-1]+' (optional, default=off) ==> high resolution for modis only (on/off)'
        print '\n\n'
    
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

        # make some parameters optional
        if 'arg2' not in locals():
            arg2 = 'not_specified'
        if 'arg3' not in locals(): #in locals() and arg3 = 'OC_suite'
            arg3 = 'OC_suite'    #arg3 = OC_suite
        if 'arg4' not in locals():
            arg4 = 'off'
        if 'arg5' not in locals():
            arg5 = 'off'
        if 'arg6' not in locals():
            arg6 = 'off'
        print arg6
        batch_proc_L12(arg1, arg2, arg3, arg4, arg5, arg6)
        

#--------------------------
#       Command Line
#--------------------------
if __name__=='__main__':
    main(*sys.argv[1:])
