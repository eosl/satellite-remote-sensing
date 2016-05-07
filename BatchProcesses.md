

# Introduction #

The original batch scripts have been updated, and some additional programs and functionality have been added, such as automatically decompressing files, MODIS hi-res processing, and functions for using NetCDF files.  The batch processing scripts now call to some external functions that are contained in addition .py files, and there is now a script to allow you to use a single call for executing Level-1 to Level-3 binned, as well as a way to save all your options right in the script.  And for those of you who never want to look at code again, we've made a GUI that allows you to run any combination of 1-2,2-3,and 1-3 processing by simply clicking a few buttons.



# Python Files and Routines #

The following scripts are included in your **Python** directory.  Included below are descriptions of what is in each .py file and how to execute the program.

## batch\_L12.py ##

**batch\_L12.py** is the main processing script for processing L1A to L2.  Currently, it can process VIIRS, SeaWiFS, MERIS, and both MODIS aqua and terra.  Additionally, for MODIS data, processing of the high resolution bands (QKK, HKM) can be completed.

This script can be executed from the command line, and the only required argument is the directory of the level-1 data.  The script can be executed as shown below:


`$ python batch_L12.py --l1a_dir=/Users/satellite/data`


The additional arguments that are optional include a level-2 output directory, a product list, NO2 on/off, SWIR on/off, and high resolution processing on/off.  To see how to assign these variables and to view the defaults, simply execute the script without any variables specified and the instructions will be printed in your command window:


`$ python batch_L12.py`


## batch\_L23.py ##

**batch\_L23.py** is the main processing script for creating level-3 binned and mapped data (straight to map is not an option in this batch execution at the moment). Currently it can process all of the same satellites as **batch\_L12**, however the ability to map high resolution MODIS data is not available in SeaDAS 7.0 at the moment, so any QKM or HKM level-2 files will be ignored when running this script.

This script can be executed from the command line, and the only required argument is the directory of the level-2 data.  The script can be executed as shown below:


`$ python batch_L23.py --l2_dir=/Users/satellite/data/L2`


Although latitude and longitude are not required, the script will map all of the files based on the coordinates of the first file it reads, which may not have the proper coordinates or match the bounds of the data found in additional files.  Therefore, it is recommended that **latlon** be specified.  The additional arguments that are optional include a level-3 output directory, a product list, the spatial resolution, time period, color flags to check, sst flags to check, standard mapped imaging projection, and Stats Yes/No.  To see how to assign these variables and to view the defaults, simply execute the script without any variables specified and the instructions will be printed in your command window:


`$ python batch_L23.py`



## Batch`_`Proc.py ##

**Batch`_`Proc.py** will allow you to directly process level-1 data to level-3 binned and mapped data and images.  By opening the script in a text editor, you will be able to edit the directories and variables necessary to process all of the data, and dictate whether you would like to process level-1 to level-2, level-2 to level-3, or directly from level-1 to level-3.  Using this script will allow you to save your personal defaults by having them set as variables directly within the script.  The script can be executed from the command line as shown below:


`$ python Batch_Proc.py`

## Batch`_`Processing`_`GUI.py ##

\begin{wrapfigure}{r}{0.5\textwidth}
\begin{center}

\includegraphics[scale=.4]{gui.png}
\end{center}
\end{wrapfigure}


**Batch`_`Processing`_`GUI.py** will allow you to do the same processing as **Batch`_`Proc.py** using a simple graphical user interface (GUI).  Open the GUI from the command line from the command line as shown below:


`$ python Batch_Processing_GUI.py`


All of the defualts, as expected by the **batch\_L12.py** and **batch\_L23.py** scripts that are executed are automatically filled in and chosen when the GUI is opened.  To specify the file directories, you can either directly type the entire directory path into the field, or simply click on the **[...]** button next to the field to browse for a folder or create a new one.  By simply selecting a level-1 directory, default names for the level-2 and level-3 directories will be created in the entry fields.

Once all of the fields necessary for the processing have been filled in, first click **`[`Apply Settings`]`** to assign your choices to their variables, and then select the button for the appropriate processing.  **Product List**, **Lat/Lon**, and **Time Period** can be specified by using a comma with no spaces to separate values, i.e., **[40,-72,46,-66]** and **DLY,WKY,MON**.


## general\_utilities.py ##

**general\_utilities.py** contains four python functions which are called by some of the other scripts and serve a certain purpose, and can also be called independently to be used on their own by simply importing the function in python or another python script such as:

```
>>> import general_utilites
>>> general_utilities.decompress_file('FILE NAME')
```

### _get\_cntr\_latlon(latlon)_ ###

This function outputs the center latitude and longitude of a given set of boundary coordinates.

### _get\_jday(file)_ ###

This function returns the Julian Day Number from a file name.

### _decompress\_file(file)_ ###

This function will decompress any file found with a .zip, .tar, .gz, or .bz2 extension, as well as unpacking multiple compressions, such as .tar.gz.

### _map\_resize(data,latitudes,longitudes,xdim,ydim)_ ###

This function is used to remap geophysical data such as sea surface height which is mapped from 0 degree longitude to 0 degree into a -180 degree to +180 degree view and resize to a specified array of dimensions **xdim** and **ydim**.  The input arguments it requires are **data** which is the array of geophysical data, a 1-dimensional array for latitudes for **latitude**, a 1-dimensional array for **longitude**, and the number of pixels for each axis as **xdim** and **ydim**.


## hdf\_utilities.py ##


**hdf\_utilities** contains multiple python functions that are used to open, read, and extract information from HDF files for use within the batch processing or as independently used functions.  The functions can be called independently by importing the function in python or another python script such as:

```
>>> import hdf_utilities
>>> hdf_utilities.read_hdf_prod('FILE NAME','PRODUCT NAME')
```

### _read\_hdf\_prod(filename, prod)_ ###

This function will read the data for a specific product from an HDF file. Specify the file name and product, and the output can be assigned to a variable, such as **chl=read\_hdf\_prod(filename,chlor\_a)**

### _get\_smi\_projection(file)_ ###

This function will output the type of map projection that was used to create the Standard Mapped Image file given.

### _get\_hdf\_latlon(file)_ ###

This function will extract the lat/lon boundaries of an HDF file.

### _get\_l2hdf\_prod(file)_ ###

This function will return a list of the products contained within an HDF file.

### _get\_sds7\_default\_l2flags(sensor\_id,prod\_type)_ ###

This function will return the default level-2 color flags for a specific satellite from the SeaDAS 7 parameter files.


## read\_utilites.py ##


**read\_utilities.py** contains multiple python functions that are used to open, read, and extract information from CDF files for use within the batch processing or as independently used functions.  The functions can be called independently by importing the function in python or another python script such as:

```
>>> import read_utilities
>>> read_utilities.read_cdf_prod('FILE NAME','PRODUCT NAME')
```

### _read\_cdf\_prod(file,prod)_ ###

This function will read the data for a specific product from netCDF file. Specify the file name and product, and the output can be assigned to a variable, such as **chl=read\_cdf\_prod(filename,chlor\_a)**

### _read\_aviso\_madt\_nc(file)_ ###

This function will read an AVISO nc file and return an array of mapped data.


## subprograms.py ##


**subprograms.py** contains a group of functions that are used within the batch processing and can be called independently by importing the function in python or another python script such as:

```
>>> import subprograms
>>> subprograms.get_prod_min_max(fname,prod)
```

### _custom\_cmap(ct)_ ###

This function outputs a python color map based on **ct**, which is an IDL parameter file.

### _get\_prod\_min\_max(fname,prod)_ ###

This function returns the default min, max, and scale (linear, logarithmic) for mapping a product based on a text file containing all of the defaults for the SeaDAS products.  The default file used for reference is **prod\_min\_max\_tab\_delimted\_txt**, contained within '/idl\_pros/dly\_wkl\_mon\_qcmasked\_pros/png\_min\_max\_settings/'.

### _write\_smi\_png(png\_fname,geophys\_img, product, latlon,proj\_name)_ ###

This function creates the PNG image files from the Standard Mapped Image HDF files.  **png\_fname** specifies the name of the output PNG file, **geophys\_img** is a 2d array of values to be imaged, **product** is the name of the product being imaged, **latlon** is an object containing the boundaries, and **proj\_name** is the projection type, such as `RECT' or `CYL'.