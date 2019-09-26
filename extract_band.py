"""
Extract and save a band from a list of tif files
Author: Maxim Chernetskiy, 2019
"""

import gdal
import os


root_dir = '/data1/imaging/overpass/c2_data/VX020001b2/'
out_dir = root_dir + '/single_band/'

# Walk through given directory tree and find all tif files
list_file = []
for roots, dirs, files in os.walk(root_dir):
	for name in files:
		if name.endswith("Stretched.tif"):
			full_path = roots + "/" + name
			list_file.append(full_path)


# Open files for writing. It's where we will write lists of output files. 
f = []
f.append(open(out_dir + 'list_blue.txt', 'w'))
f.append(open(out_dir + 'list_green.txt', 'w'))
f.append(open(out_dir + 'list_red.txt', 'w'))
			
# Extract bands using gdal
bands = ['blue', 'green', 'red']
for i in range(0, len(list_file), 10):
	print 'Opening ', list_file[i]
	gds = gdal.Open(list_file[i])
	for b in range(3):
		band_in = gds.GetRasterBand(b+1)
		img = band_in.ReadAsArray()
		driver = gds.GetDriver()
		name_out = list_file[i].split("/")[-1].split(".")[0] + "_" + bands[b]  + ".tif"
		if os.path.isdir(out_dir) == False:
			os.mkdir(out_dir)
        
		gds_out = driver.Create(out_dir + name_out, gds.RasterXSize, gds.RasterYSize, 1, band_in.DataType)
	
		band_out = gds_out.GetRasterBand(1)
		band_out.WriteArray(img)
		gds_out = None
		# Write output file name to txt file
		f[b].write(out_dir + name_out + "\n")
	
	gds = None

for i in range(3):
	f[i].close()

# overpass/c2_data/VX020001b2/001/VX020001b2_001_00_L1A_Stretched.tif
