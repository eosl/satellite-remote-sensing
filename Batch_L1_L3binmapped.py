#! /usr/bin/env python

import batch_L12
import batch_L23
import sys, os
import getopt

sys.dont_write_bytecode = True


if __name__=='__main__':
    args = sys.argv[1:]
    arg_options = ['l1a_dir=', 'l2_dir=','binmap_dir=', 'prod_list=','latlon=', 'space_res=', 'time_period=','hires=','smi_proj=','color_flags=', 'sst_flags=', 'stats_yesno=','NO2_onoff=', 'swir_onoff',]
    opts, arg = getopt.getopt(args, '', arg_options)

    if len(args) == 0:
        print '\n Usage:\n\t Batch_L1_L3binmapped.py --l1a_dir=<l1a_dir> --l2_dir=<l2_dir> --binmap_dir=<l3_dir> --prod_list=<prod1,prod2,prod3,...> --latlon=<S,W,N,E>--space_res=<space_res> --time_period=<time_period> --hires=<on/off> --smi_proj=<smi_proj> --color_flags=<flag1,flag2,...> --sst_flags=<flag1,flag2,...>   --stats_yesno=<stats_yesno> --NO2_onoff=<NO2_onoff> --swir_onoff=<swir_onoff>\n\n'
        print '\t--'+arg_options[0][:-1]+' (required) ==> directory containing Level 1 data files'
        print '\t--'+arg_options[1][:-1]+' (optional, default=l1a_dir/L2_files) ==> new directory that the l2 data files will be written to'
        print '\t--'+arg_options[2][:-1]+' (optional, default=l1a_dir/L3_binmap) ==> new directory that the l2bin and l3bin data files will be written to'
        print '\t--'+arg_options[3][:-1]+' (optional, default=OC_suite) products to be processed to L2, binned, and mapped to smi and png'
        print '\t--'+arg_options[4][:-1]+' (optional, default=whole image) ==> Lat/LON --S,W,N,E'
        print '\t--'+arg_options[5][:-1]+' (optional, default=9) ==> Spatial Resolution in km (1,4,9,36)'
        print '\t--'+arg_options[6][:-1]+' (optional, defualt=DLY) ==> Time period to be averages (DLY, WKY, MON)'
        print '\t--'+arg_options[7][:-1]+' (optional, defualt=off) ==> Hires processing for 500m and 250m MODIS bands (on/off)'
        print '\t--'+arg_options[8][:-1]+' (optional, defualt=RECT) ==> SMI projection (RECT = rectangular, SIN = sinusoidal)'
        print '\t--'+arg_options[9][:-1]+' (optional, defualt=standard) ==> Color flags to check'
        print '\t--'+arg_options[10][:-1]+' (optional, defualt=standard) ==> SST flags to check'
        print '\t--'+arg_options[11][:-1]+' (optional, defualt=no) ==> Stats Yes/No'
        print '\t--'+arg_options[12][:-1]+' (optional, defualt=off) ==>  Nitrogen Dioxide transmittance bitmask selector (on/off)'
        print '\t--'+arg_options[13][:-1]+' (optional, defualt=off) ==> aerosol mode option (on/off)'
    else:
        for option,value in opts:
            if option == '--' + arg_options[0][:-1]:
                arg1 =  value
            if option == '--' + arg_options[1][:-1]:
                arg2 =  value
            if option == '--' + arg_options[2][:-1]:
                arg3 = value
            if option == '--' + arg_options[3][:-1]:
                arg4 =  value
            if option == '--' + arg_options[4][:-1]:
                arg5 = value
            if option == '--' + arg_options[5][:-1]:
                arg6 = value
            if option == '--' + arg_options[6][:-1]:
                arg7 =  value
            if option == '--' + arg_options[7][:-1]:
                arg8 =  value
            if option == '--' + arg_options[8][:-1]:
                arg9 = value
            if option == '--' + arg_options[9][:-1]:
                arg10 =  value
            if option == '--' + arg_options[10][:-1]:
                arg11 =  value
            if option == '--' + arg_options[11][:-1]:
                arg12 =  value
            if option == '--' + arg_options[12][:-1]:
                arg13 =  value
            if option == '--' + arg_options[13][:-1]:
                arg14 =  value
        if 'arg2' not in locals():
            if arg1[-1] == '/':
                arg1 = arg1[:-1]
            if arg1[0] == '~':
                arg1 = os.path.expanduser(arg1)                
            arg2 =  os.path.dirname(arg1) + '/L2_files'
        if 'arg4' in locals():
            arg4 = arg4.split(',') #split products into list (chlor_a,sst,...)
        if 'arg7' in locals():
            arg7 = arg7.split(',') #split averages into list (DLY,WKY,MON)
        if 'arg5' in locals():
            arg5 = arg5.split(',') #split latlon into list (south,west,north,east)

        
        args_l12 = {'l1a_dir':arg1}
        if 'arg2' in locals():
            args_l12.update({'l2_dir':arg2})
        if 'arg4' in locals():
            args_l12.update({'prod_list':arg4})
        if 'arg13' in locals():
            args_l12.update({'NO2_onoff':arg13})
        if 'arg14' in locals():
            args_l12.update({'swir_onoff':arg14})
        if 'arg8' in locals():
            args_l12.update({'hires':arg8})
        batch_L12.batch_proc_L12(**args_l12)

        
        args_l23 = {'l2dir':arg2}
        if 'arg3' in locals():
            args_l23.update({'output_dir':arg3})
        if 'arg4' in locals():
            args_l23.update({'products':arg4})
        if 'arg6' in locals():
            args_l23.update({'space_res':arg6})
        if 'arg7' in locals():
            args_l23.update({'time_period':arg7})
        if 'arg10' in locals():
            args_l23.update({'color_flags_to_check':arg10})
        if 'arg11' in locals():
            args_l23.update({'sst_flags_to_check':arg11})
        if 'arg5' in locals():
            args_l23.update({'latlon':arg5})
        if 'arg9' in locals():
            args_l23.update({'smi_proj':arg9})
        if 'arg12' in locals():
            args_l23.update({'stats_yesno':arg12})
        
        batch_L23.batch_proc_L23(**args_l23)


