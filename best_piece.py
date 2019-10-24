import gdal
import numpy as np
from scipy import interpolate
from scipy import stats
import glob

# from sklearn.linear_model import LinearRegression

# def find_file():
#     # from pathlib import Path
#
#     for filename in Path('src').glob('**/*.c'):
#         print(filename)


band = 'blue'

def interp(arr_2d_1, arr_2d_2):
    """
    Interpolate array arr_2d_1 to the size of arr_2d_2

    :param arr_2d_1: array
    :param arr_2d_2: array
    :return: array
    """

    x = np.arange(0, arr_2d_1.shape[1])
    y = np.arange(0, arr_2d_1.shape[0])
    f = interpolate.interp2d(x, y, arr_2d_1, kind='cubic')

    step_x = arr_2d_1.shape[1] / np.double(arr_2d_2.shape[1])
    step_y = arr_2d_1.shape[0] / np.double(arr_2d_2.shape[0])

    xnew = np.arange(0, arr_2d_1.shape[1], step_x)
    ynew = np.arange(0, arr_2d_1.shape[0], step_y)
    arr_new = f(xnew, ynew)


    return arr_new



#dir_in_ref = '/data1/imaging/magigan_and_caspgo/MAGiGAN/Res_VX020001eb_s/red/Refined/'
#f_in_ref = 'SRR_n92.tif'


dir_in_ref = '/data1/imaging/overpass/output/out_srr_VX020001b2/' + band + '/Refined/'
f_in_ref = 'SRR_n14.tif'


#dir_in = '/Users/max/satellite/carbonite-2/output/out_srr_VX020001eb/'
#f_in = 'VX020001eb_004_00_L1A_Stretched_green_sub.tif'

#dir_in = '/data1/imaging/overpass/c2_data/VX020001eb/single_band_sub/'
dir_in = '/data1/imaging/overpass/c2_data/VX020001b2/single_band_sub/'

#dir_out = '/Users/max/satellite/carbonite-2/output/out_srr_VX020001eb/green_orig/'

dir_out = 'img_VX020001b2/'

# f_list = glob.glob(dir_in + '**/SRR*.tif')

print(dir_in + 'VX020001b2_*_*_L1A_Stretched_' + band + '_sub.tif')

f_list = glob.glob(dir_in + 'VX020001b2_*_*_L1A_Stretched_' + band + '_sub.tif')

gds_ref = gdal.Open(dir_in_ref + f_in_ref)
img_ref = gds_ref.GetRasterBand(1).ReadAsArray()


# gds_in = gdal.Open(dir_in + f_in)
# band = gds_in.GetRasterBand(1)
# type_in = band.DataType
# img = band.ReadAsArray()
# x_size = img.shape[1]
# y_size = img.shape[0]

ssize = 64



driver = gdal.GetDriverByName('GTiff')

r_val_arr0 = []
i_arr0 = []
j_arr0 = []

for ff in f_list:
    k = 0
    r_val_arr = []
    i_arr = []
    j_arr = []

    gds_in = gdal.Open(ff)
    gds_band = gds_in.GetRasterBand(1)
    type_in = gds_band.DataType
    img = gds_band.ReadAsArray()
    x_size = img.shape[1]
    y_size = img.shape[0]
    n = x_size / ssize
    m = y_size / ssize

    for i in range(0, x_size, ssize):
        for j in range(0, y_size, ssize):

            img_s = img[i:i + ssize, j:j + ssize]
            img_ss = interp(img_s, img_ref)

            slope, intercept, r_value, p_value, std_err = stats.linregress(img_ref.flatten(), img_ss.flatten())

            r_val_arr = np.append(r_val_arr, r_value)
            i_arr = np.append(i_arr, i)
            j_arr = np.append(j_arr, j)

            k += 1
    opti = i_arr[r_val_arr.argmax()].astype(int)
    optj = j_arr[r_val_arr.argmax()].astype(int)

    img_opt = img[opti:opti + ssize, optj:optj + ssize]

    gds_out = driver.Create(dir_out + 'SRR_n%d_opt.tif' % r_val_arr.argmax(), ssize, ssize, 1, type_in)
    # gds_out.GetRasterBand(1).WriteArray(img[j:j+ssize, i:i+ssize])
    gds_out.GetRasterBand(1).WriteArray(img_opt)
    gds_out = None

    i_arr0 = np.append(i_arr0, opti)
    j_arr0 = np.append(j_arr0, optj)
    r_val_arr0 = np.append(r_val_arr0, r_val_arr.max())

    print(r_val_arr.argmax(), r_val_arr.max(), ff, opti, optj)

gds_out0 = gdal.Open(f_list[np.argmax(r_val_arr0)])
gds_band = gds_out0.GetRasterBand(1)
type_in = gds_band.DataType
img = gds_band.ReadAsArray()
ii = i_arr0[r_val_arr0.argmax()].astype(int)
jj = j_arr0[r_val_arr0.argmax()].astype(int)
img_opt0 = img[ii:ii + ssize, jj:jj + ssize]
gds_out = driver.Create(dir_out + 'SRR_n%d_opt_opt_%s.tif' % (r_val_arr0.argmax(), band), ssize, ssize, 1, type_in)
# gds_out.GetRasterBand(1).WriteArray(img[j:j+ssize, i:i+ssize])
gds_out.GetRasterBand(1).WriteArray(img_opt0)
gds_out = None

print(r_val_arr0.argmax(), r_val_arr0.max(), f_list[r_val_arr0.argmax()], ii, jj)

print r_val_arr0.argmax()

gds = None
