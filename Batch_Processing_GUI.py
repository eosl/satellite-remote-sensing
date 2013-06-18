#! /usr/bin/env python

##################################################
#### Created By Robert Levine and Nick Nardelli###
#### Created on 6/13/13, Last Edited: 6/13/13 ####
##################################################
#  To launch the GUI, type the following from the terminal
#  $ python Batch_Processing_GUI.py
##################################################

import sys
sys.path.insert(0, 'utilities')

import batch_L23
import batch_L12
import os, sys

from Tkinter import *
from tkFileDialog import askdirectory

sys.dont_write_bytecode = True

values={'l1a_dir':None,'l2_dir':'not_specified','output_dir':None,'prod_list':None,'latlon':None,'space_res':None,'time_period':None,'hires':None,'l2prod_list':None,
    'color_flags':None,'sst_flags':None,'stats_yesno':None,'NO2_onoff':None,'swir_onoff':None,'smi_proj':None}

values12 = {}
values23 = {}

def setupwin():

    setupwin=Tk()
    setupwin.title("Batch Processing")
    questionframe=Frame(setupwin)
    questionframe.grid(column=0,row=0)

    g = StringVar()
    h = StringVar()
    j = StringVar()
    def variables(key, value):
        values[key]=value

#    def directory(key):
#        dir =  askdirectory()
#        g.set(dir)
##        variables(key, dir)
    def apply_all():
        l1= l1_label.get()
        variables('l1a_dir',l1)
        l2= l2_label.get()
        variables('l2_dir',l2)
        l3= binmap_label.get()
        variables('output_dir',l3)
        p = prod_list.get()
        variables('prod_list',p)
        l2p = l2prod_list.get()
        variables('l2prod_list',l2p.split(','))
        ll= latlon.get()
        variables('latlon',ll.split(','))
        sr = srvar.get()
        variables('space_res',sr)
        t = time_period.get()
        variables('time_period',t.split(','))
        hr = hrvar.get()
        variables('hires',hr)
        smi = smivar.get()
        variables('smi_proj',smi)
        cf = color_flags.get()
        variables('color_flags',cf)
        sf = sst_flags.get()
        variables('sst_flags',sf)
        st = statsvar.get()
        variables('stats_onoff',st)
        N = NO2var.get()
        variables('NO2_onoff',N)
        sw = swirvar.get()
        variables('swir_onoff',sw)
        global values12
        values12 = {'l1a_dir':values['l1a_dir'],'l2_dir':values['l2_dir'],'prod_list':values['prod_list'],'NO2_onoff':values['NO2_onoff'],
            'swir_onoff':values['swir_onoff'],'hires':values['hires']}
        
        global values23
        values23 = {'l2dir':values['l2_dir'],'output_dir':values['output_dir'],'products':values['l2prod_list'],'space_res':values['space_res'],
            'time_period':values['time_period'],'color_flags_to_check':values['color_flags'],'sst_flags_to_check':values['sst_flags'],
            'latlon':values['latlon'],'smi_proj':values['smi_proj'], 'stats_yesno':values['stats_yesno']}

#    def prints():
#        print values12
#        print values23
    def setall():
        directory = askdirectory()
        g.set(directory)
        h.set(os.path.dirname(directory) + '/L2')
        j.set(os.path.dirname(directory) + '/L3')
    
   
    l1dir=Button(questionframe, text = '...', command=setall)
    l1dir.grid(column=1,row=1, sticky='e')
    l1_label = Entry(questionframe, width=20, textvariable=g)
    l1_label.grid(column=1, row=1, sticky='w')
    l1dirLabel=Label(questionframe,text="Level-1 Directory")
    l1dirLabel.grid(column=0,row=1)

    
    l2dir=Button(questionframe, text = '...', command=lambda: h.set(askdirectory()))
    l2dir.grid(column=1,row=2, sticky='e')
    l2_label = Entry(questionframe, width=20, textvariable=h)
    l2_label.grid(column=1, row=2, sticky='w')
    l2dirLabel=Label(questionframe,text="Level-2 Directory")
    l2dirLabel.grid(column=0,row=2)

    binmap_dir=Button(questionframe, text = '...', command=lambda: j.set(askdirectory()))
    binmap_dir.grid(column=1,row=3, sticky='e')
    binmap_label = Entry(questionframe, width=20, textvariable=j)
    binmap_label.grid(column=1, row=3, sticky='w')
    binmap_dirLabel=Label(questionframe,text="Level-3 Directory")
    binmap_dirLabel.grid(column=0,row=3)

    prod_list=Entry(questionframe,width=30)
    prod_list.insert(0, 'OC_suite')
    prod_list.grid(column=1,row=4)
    prod_listLabel=Label(questionframe,text="L1 to L2 Product List")
    prod_listLabel.grid(column=0,row=4)

    l2prod_list=Entry(questionframe,width=30)
    l2prod_list.insert(0, 'all')
    l2prod_list.grid(column=1,row=5)
    l2prod_listLabel=Label(questionframe,text="L2 to L3 Product List")
    l2prod_listLabel.grid(column=0,row=5)
    
    latlon=Entry(questionframe,width=30)
    latlon.insert(0,'whole')
    latlon.grid(column=1,row=6)
    latlonLabel=Label(questionframe,text="Lat/Lon")
    latlonLabel.grid(column=0,row=6)

    res_opts = ['1','2','4','9','36']
    srvar = StringVar()
    srvar.set(res_opts[3]) #Default is 9km
    space_res = OptionMenu(questionframe,srvar,*res_opts)
    space_res.grid(column=1,row=7, sticky = 'ew', padx=2, pady=2)
    space_resLabel=Label(questionframe,text="Spatial Resolution")
    space_resLabel.grid(column=0,row=7)

    time_period=Entry(questionframe,width=30)
    time_period.insert(0,'DLY')
    time_period.grid(column=1,row=8)
    time_periodLabel=Label(questionframe,text="Time Period")
    time_periodLabel.grid(column=0,row=8)

    hires_opts = ['on','off']
    hrvar = StringVar()
    hrvar.set(hires_opts[1]) #Default is off
    hires=OptionMenu(questionframe,hrvar,*hires_opts)
    hires.grid(column=1,row=9, sticky = 'ew', padx=2, pady=2)
    #hires.grid(column=1,row=8)
    hiresLabel=Label(questionframe,text="Hi-Res (MODIS only)")
    hiresLabel.grid(column=0,row=9)
    
    smi_opts = ['RECT','SIN']
    smivar=StringVar()
    smivar.set(smi_opts[0]) #Default is RECT
    smi_proj = OptionMenu(questionframe, smivar,*smi_opts)
    smi_proj.grid(column=1,row=10, sticky = 'ew', padx=2, pady=2)
    #smi_proj.grid(column=1,row=9)
    smi_projLabel=Label(questionframe,text="SMI Projection")
    smi_projLabel.grid(column=0,row=10)
    
    color_flags=Entry(questionframe,width=30)
    color_flags.insert(0,'standard')
    color_flags.grid(column=1,row=11)
    color_flagsLabel=Label(questionframe,text="Color Flags to Check")
    color_flagsLabel.grid(column=0,row=11)
    
    sst_flags=Entry(questionframe,width=30)
    sst_flags.insert(0,'standard')
    sst_flags.grid(column=1,row=12)
    sst_flagsLabel=Label(questionframe,text="SST Flags to Check")
    sst_flagsLabel.grid(column=0,row=12)
    
    stats_opts = ['on','off']
    statsvar= StringVar()
    statsvar.set(stats_opts[1]) #Default is off
    stats_yesno=OptionMenu(questionframe, statsvar,*stats_opts)
    stats_yesno.grid(column=1,row=13, sticky = 'ew', padx=2, pady=2)
    #stats_yesno.grid(column=1,row=12)
    stats_yesnoLabel=Label(questionframe,text="Stats Yes/No")
    stats_yesnoLabel.grid(column=0,row=13)

    NO2_opts = ['on','off']
    NO2var= StringVar()
    NO2var.set(NO2_opts[1]) #Default is off
    NO2_yesno=OptionMenu(questionframe, NO2var,*NO2_opts)
    NO2_yesno.grid(column=1,row=14, sticky = 'ew', padx=2, pady=2)
    #NO2_onoff.grid(column=1,row=13)
    NO2_onoffLabel=Label(questionframe,text="Nitrogen Dioxide On/Off")
    NO2_onoffLabel.grid(column=0,row=14)

    swir_opts = ['on','off']
    swirvar= StringVar()
    swirvar.set(swir_opts[1]) #Default is off
    swir_onoff=OptionMenu(questionframe, swirvar,*swir_opts)
    swir_onoff.grid(column=1,row=15, sticky = 'ew', padx=2, pady=2)
    #swir_onoff.grid(column=1,row=14)
    swir_onoffLabel=Label(questionframe,text="SWIR On/Off")
    swir_onoffLabel.grid(column=0,row=15)



    def level1_to_3():
        batch_L12.batch_proc_L12(**values12)
        batch_L23.batch_proc_L23(**values23)
    def level2_to_3():
        batch_L23.batch_proc_L23(**values23)
    def level1_to_2():
        batch_L12.batch_proc_L12(**values12)


    RunButton=Button(questionframe,text="Apply Settings",command=apply_all)
    RunButton.grid(column=0,row=16)
#    RunButton=Button(questionframe,text="print Settings",command=lambda: prints())
#    RunButton.grid(column=1,row=20)
    RunButton=Button(questionframe,text="Process Level 1 to 2",command=level1_to_2)
    RunButton.grid(column=0,row=17)
    RunButton=Button(questionframe,text="Process Level 2 to 3 (binmapped)",command=level2_to_3)
    RunButton.grid(column=1,row=16)
    RunButton=Button(questionframe,text="Process Level 1 to 3 (binmapped)",command=level1_to_3)
    RunButton.grid(column=1,row=17)

    for child in questionframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    setupwin.mainloop()

setupwin()
