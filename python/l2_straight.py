#! /usr/bin/env python

import sys, os
import glob
import numpy as n
sys.dont_write_bytecode = True
sys.path.insert(0, 'utilities')

import subprograms as sp
import hdf_utilities as hu
import general_utilities as gu

class Coords():
    north = 0
    south = 0
    east = 0
    west = 0
    
    


def batch_straight(in_dir, out_dir='not_specified', products=['all']):
    
    # make sure directories are right (/ and ~)
    in_dir = gu.path_reformat(in_dir)
    out_dir = gu.path_reformat(out_dir)
    
    if out_dir == 'not_specified':
        out_dir = os.path.dirname(in_dir) + '/straight_pngs'
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    
    filelist = n.asarray(glob.glob(in_dir + '/*'))
    
    
    for file in filelist:     
        
        # only for files with products
        if len(hu.get_l2hdf_prod(file)) > 0:
            
            file_base = os.path.basename(file)
            coords = hu.get_hdf_latlon(file)
            prodlist = gu.get_product_list(file, products)
         
            for prod in prodlist:
                png_out = out_dir + '/' + file_base[:14] + '-' + prod + '.png'

                data = hu.read_hdf_prod(file, prod)
                sp.write_png(png_out, data, prod, coords, 'RECT')
                
              
              
              
#
# defaults
#   
def main(*args):
    import getopt
    
    arg_options = ['l2_dir=', 'png_dir=', 'products=']
    opts, arg = getopt.getopt(args, '', arg_options)
    
    if len(args) == 0: 
        print '\nUsage:\n\t l2_straight.py --l2_dir=<l2_dir> --png_dir=<png_dir> --products=<prod1,prod2,prod3>\n'
        print '\t--'+arg_options[0][:-1] + ' ==> input directory containing Level 2 files'
        print '\t--'+arg_options[1][:-1] + ' ==> output directory where png file will be put'
        print '\t--'+arg_options[2][:-1] + ' ==> list of comma-separated products (chlor_a,cdom_index,...)\n'
    else:
        for option,value in opts:
            if option == '--' + arg_options[0][:-1]:
                arg1 = value
            if option == '--' + arg_options[1][:-1]:
                arg2 = value
            if option == '--' + arg_options[2][:-1]:
                arg3 = value

        arglist = {}
        if 'arg1' in locals():
            arglist.update({'in_dir':arg1})
        if 'arg2' in locals():
            arglist.update({'out_dir':arg2})
        if 'arg3' in locals():
            arg3 = arg3.split(',')
            arglist.update({'products':arg3})  
        
    
        batch_straight(**arglist)  

 

#
# COMMAND LINE CALL
#
if __name__=='__main__':
    
    main(*sys.argv[1:])