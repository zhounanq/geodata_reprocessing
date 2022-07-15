# -*- coding: utf-8 -*-

"""

"""
import os, sys
import time
import datetime
import argparse
import numpy as np
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from osgeo import gdal, osr

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
gdal.UseExceptions()


def parse_args():
    parser = argparse.ArgumentParser(description='Raster fusion using two temporal images')
    parser.add_argument('--r1-path', required=False, type=str,
                        default="./data/r1.tif",
                        help='ref raster file 1 in TIFF format')
    parser.add_argument('--r2-path', required=False, type=str,
                        default="./data/r2.tif",
                        help='ref raster file 2 in TIFF format')
    parser.add_argument('--r-path', required=False, type=str,
                        default="./data/r.tif",
                        help='source raster file in TIFF format')
    parser.add_argument('--mask-path', required=False, type=str,
                        default="./data/mask.tif",
                        help='mask raster file in TIFF format')
    parser.add_argument('--result-path', required=False, type=str,
                        default="2",
                        help='result raster file in TIFF format')
    opts = parser.parse_args()
    return opts


def read_raster1(raster1_path):

    print("### Reading t1 image {}".format(raster1_path))
    # 1. open source data
    raster1_ds = gdal.Open(raster1_path, gdal.GA_ReadOnly)
    if not raster1_ds:
        print('Unable to open image {}'.format(raster1_path))
        sys.exit(1)

    raster1_proj = raster1_ds.GetProjection()
    raster1_geotransform = raster1_ds.GetGeoTransform()
    raster1_datatype = raster1_ds.GetRasterBand(1).DataType
    raster1_shape = (raster1_ds.RasterXSize, raster1_ds.RasterYSize, raster1_ds.RasterCount)

    # 2. get data
    raster1_array = raster1_ds.ReadAsArray()

    # 3. return
    print("### Reading over")
    return raster1_array


def read_raster2(raster2_path):

    print("### Reading t2 image {}".format(raster2_path))
    # 1. open source data
    raster2_ds = gdal.Open(raster2_path, gdal.GA_ReadOnly)
    if not raster2_ds:
        print('Unable to open image {}'.format(raster2_path))
        sys.exit(1)

    raster2_proj = raster2_ds.GetProjection()
    raster2_geotransform = raster2_ds.GetGeoTransform()
    raster2_datatype = raster2_ds.GetRasterBand(1).DataType
    raster2_shape = (raster2_ds.RasterXSize, raster2_ds.RasterYSize, raster2_ds.RasterCount)

    # 2. get data
    raster2_array = raster2_ds.ReadAsArray()

    # 3. return
    print("### Reading over")
    return raster2_array


def read_target_raster(raster_path, mask_path):

    print("### Reading target image {}".format(raster_path))
    #################################################################
    # 1. open source data
    raster_ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
    if not raster_ds:
        print('Unable to open image {}'.format(raster_path))
        sys.exit(1)
    raster_proj = raster_ds.GetProjection()
    raster_geotransform = raster_ds.GetGeoTransform()
    raster_datatype = raster_ds.GetRasterBand(1).DataType
    raster_shape = (raster_ds.RasterXSize, raster_ds.RasterYSize, raster_ds.RasterCount)
    # 2. get data
    raster_array = raster_ds.ReadAsArray()

    #################################################################
    mask_ds = gdal.Open(mask_path, gdal.GA_ReadOnly)
    if not mask_ds:
        print('Unable to open image {}'.format(mask_path))
        sys.exit(1)
    mask_proj = mask_ds.GetProjection()
    mask_geotransform = mask_ds.GetGeoTransform()
    mask_datatype = mask_ds.GetRasterBand(1).DataType
    mask_shape = (mask_ds.RasterXSize, mask_ds.RasterYSize, mask_ds.RasterCount)
    # 2. get data
    mask_array = mask_ds.ReadAsArray()

    #################################################################
    # 3. return
    print("### Reading over")
    return raster_array, mask_array


def reshape_array_for_train(r1_array, r2_array, target_array, mask_array):

    print("### Reconstructing array for training....")

    raster_shape = r1_array.shape # band, row, col

    row_array, col_array = np.nonzero(100-mask_array)
    train_pixel_count = row_array.size

    train_array_re = np.zeros((train_pixel_count, raster_shape[0]*2))
    label_array_re = np.zeros((train_pixel_count, raster_shape[0]))

    for pp in range(0, train_pixel_count):
        r1_pixel = r1_array[ : , row_array[pp] , col_array[pp]]
        r2_pixel = r2_array[ : , row_array[pp] , col_array[pp]]
        label_pixel = target_array[ : , row_array[pp] , col_array[pp]]

        train_array_re[pp, : raster_shape[0]] = r1_pixel[ : raster_shape[0]]
        train_array_re[pp, raster_shape[0] :] = r2_pixel[ : raster_shape[0]]
        label_array_re[pp, :] = label_pixel[ : ]
    # for

    print("### Reconstructing over")
    return train_array_re, label_array_re


def reshape_array_for_predict(r1_array, r2_array, mask_array):

    print("### Reconstructing array for predicting....")
    raster_shape = r1_array.shape # band, row, col

    row_array, col_array = np.nonzero(mask_array)
    predict_pixel_count = row_array.size

    predict_array_re = np.zeros((predict_pixel_count, raster_shape[0]*2))

    for pp in range(0, predict_pixel_count):
        r1_pixel = r1_array[ : , row_array[pp] , col_array[pp]]
        r2_pixel = r2_array[ : , row_array[pp] , col_array[pp]]

        predict_array_re[pp, : raster_shape[0]] = r1_pixel[ : raster_shape[0]]
        predict_array_re[pp, raster_shape[0] :] = r2_pixel[ : raster_shape[0]]
    # for

    print("### Reconstructing over")
    return predict_array_re, row_array, col_array


def construct_model(train_array_re, label_array_re):

    print('### Constructing and training model...')

    train_x, valid_x, train_y, valid_y = train_test_split(train_array_re, label_array_re, shuffle=True,
                                                          test_size=0.2, random_state=100)
    train_count, valid_count = int(train_x.shape[0] * 0.5), int(valid_x.shape[0] * 0.2)

    rfr = RandomForestRegressor(oob_score=True, random_state=10)
    rfr.fit(train_x[:train_count], train_y[:train_count])
    print('### Overall accuracy is {} for training'.format(rfr.oob_score_))

    test_accuracy = rfr.score(valid_x[:valid_count], valid_y[:valid_count])
    print('### Overall accuracy is {} for validation'.format(test_accuracy))

    print('### Constructing and training over')
    return rfr


def model_predict(model, predict_array_re):

    print('### Predicting with trained model...')

    predict_result = model.predict(predict_array_re)

    print('### Predicting over')
    return predict_result


def clear_prediction_mosaic(target_array, predict_result, row_array, col_array):

    print('### Mosaicing prediction with clear image...')

    pixel_count = row_array.size
    for pp in range(0, pixel_count):
        target_array[:, row_array[pp] , col_array[pp]] = predict_result[pp, :]
    # for

    print('### Mosaicing over')
    return target_array


def write_raster_with_ref(raster_array, result_path, ref_path, format='GTiff'):

    print('### Writing result image...')

    #################################################################
    # 1. open source data
    ref_ds = gdal.Open(ref_path, gdal.GA_ReadOnly)
    if not ref_ds:
        print('Unable to open image {}'.format(ref_path))
        sys.exit(1)
    raster_proj = ref_ds.GetProjection()
    raster_geotransform = ref_ds.GetGeoTransform()
    raster_datatype = ref_ds.GetRasterBand(1).DataType
    raster_shape = (ref_ds.RasterXSize, ref_ds.RasterYSize, ref_ds.RasterCount)

    #################################################################
    # 3. write image
    raster_driver = gdal.GetDriverByName(format)
    raster_ds = raster_driver.Create(result_path, xsize=raster_shape[0], ysize=raster_shape[1],
                                     bands=raster_shape[2], eType=raster_datatype)
    if not raster_ds:
        print("Unable to create image {} with driver {}".format(result_path, format))
        sys.exit(1)

    raster_ds.SetGeoTransform(raster_geotransform)
    raster_ds.SetProjection(raster_proj)

    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    raster_ds.WriteRaster(0, 0, raster_shape[0], raster_shape[1], raster_array.tobytes())

    #################################################################
    # 4. close
    raster_ds.FlushCache()
    del raster_ds, ref_ds

    print("### Success @ write_raster_with_ref() ##################")


def main_fusion():

    ###########################################################
    # cmd line
    # opts = parse_args()
    # raster1_path = opts.r1_path
    # raster2_path = opts.r2_path
    # raster_path = opts.r_path
    # mask_path = opts.mask_path
    # result_path = opts.result_path

    raster1_path = r'G:\tongnan\S2A_MSIL2A_20220411_R061_T48RWU_10m.tif'
    raster2_path = r'G:\tongnan\S2B_MSIL2A_20220426_R061_T48RWU_10m.tif'
    raster_path = r'G:\tongnan\S2A_MSIL2A_20220421_R061_T48RWU_10m.tif'
    mask_path = r'G:\tongnan\S2A_MSIL2A_20220421_cloud_mask_2.tif'
    result_path = r'G:\tongnan\S2A_MSIL2A_20220421_R061_T48RWU_10m_ml.tif'

    ###########################################################
    # do
    r1_array = read_raster1(raster1_path)
    r2_array = read_raster2(raster2_path)
    raster_array, mask_array = read_target_raster(raster_path, mask_path)

    train_array_re, label_array_re = reshape_array_for_train(r1_array, r2_array, raster_array, mask_array)
    model = construct_model(train_array_re, label_array_re)

    predict_array_re, row_array, col_array = reshape_array_for_predict(r1_array, r2_array, mask_array)
    predict_result = model_predict(model, predict_array_re)

    target_array = clear_prediction_mosaic(raster_array, predict_result, row_array, col_array)
    write_raster_with_ref(target_array, result_path, raster_path)

    ###########################################################
    # close
    print("### Task over #############################################")


def main():
    print("######################################################################################")
    print("### Raster fusion using two temporal images ##########################################")
    print("######################################################################################")

    main_fusion()

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
