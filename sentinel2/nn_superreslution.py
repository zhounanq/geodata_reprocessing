# -*- coding: utf-8 -*-

"""
Functions for image operation in gdal

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys
import time
import datetime
import argparse
import numpy as np
from osgeo import gdal, osr

os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
gdal.UseExceptions()


def parse_args():
    parser = argparse.ArgumentParser(description='Super resolution using nearest neighbour scaling')
    parser.add_argument('--src-path', required=False, type=str,
                        default="./data/random.xml",
                        help='source (input) raster file in TIFF format')
    parser.add_argument('--target-path', required=False, type=str,
                        default="./data/target.tif",
                        help='target raster file in TIFF format')
    parser.add_argument('--res-scale', required=False, type=str,
                        default="2",
                        help='scale for resolution in [2,3,6]')
    opts = parser.parse_args()
    return opts


def ndarray_nearest_neighbour_scaling(label, scale_h=2, scale_w=2):
    """
    Implement nearest neighbour scaling for ndarray
    :param label: [H, W] or [H, W, C]
    :return: label_new: [new_h, new_w] or [new_h, new_w, C]
    Examples
    --------
    ori_arr = np.array([[1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 9]], dtype=np.int32)
    new_arr = ndarray_nearest_neighbour_scaling(ori_arr, scale_h=3, scale_w=3)
    >> print(new_arr)
    [[1 1 1 2 2 2 3 3 3]
     [1 1 1 2 2 2 3 3 3]
     [1 1 1 2 2 2 3 3 3]
     [4 4 4 5 5 5 6 6 6]
     [4 4 4 5 5 5 6 6 6]
     [4 4 4 5 5 5 6 6 6]
     [7 7 7 8 8 8 9 9 9]
     [7 7 7 8 8 8 9 9 9]
     [7 7 7 8 8 8 9 9 9]]
    """

    src_h, src_w = label.shape[0], label.shape[1]
    new_h = src_h * scale_h
    new_w = src_w * scale_w

    if len(label.shape) == 2:
        label_new = np.zeros([new_h, new_w], dtype=label.dtype)
    else:
        label_new = np.zeros([new_h, new_w, label.shape[2]], dtype=label.dtype)

    y_pos = np.arange(new_h)
    x_pos = np.arange(new_w)
    y_pos = np.floor(y_pos / scale_h).astype(np.int32)
    x_pos = np.floor(x_pos / scale_w).astype(np.int32)

    y_pos = y_pos.reshape(y_pos.shape[0], 1)
    y_pos = np.tile(y_pos, (1, new_w))
    x_pos = np.tile(x_pos, (new_h, 1))
    assert y_pos.shape == x_pos.shape

    label_new[:, :] = label[y_pos[:, :], x_pos[:, :]]
    return label_new


def nn_supres_20_10(raster20_path, raster10_path, super_scale=2, format='GTiff'):
    """

    """

    #################################################################
    # 1. open source data
    raster20_ds = gdal.Open(raster20_path, gdal.GA_ReadOnly)
    if not raster20_ds:
        print('Unable to open image {}'.format(raster20_path))
        sys.exit(1)

    raster20_proj = raster20_ds.GetProjection()
    raster20_geotransform = raster20_ds.GetGeoTransform()
    data_type = raster20_ds.GetRasterBand(1).DataType
    raster20_shape = (raster20_ds.RasterXSize, raster20_ds.RasterYSize, raster20_ds.RasterCount)

    #################################################################
    # 2. get data
    raster20_array = raster20_ds.ReadAsArray()
    raster10_array = ndarray_nearest_neighbour_scaling(raster20_array, super_scale, super_scale)

    #################################################################
    # 3. write image
    raster10_driver = gdal.GetDriverByName(format)
    raster10_shape = (raster20_shape[0]*super_scale, raster20_shape[1]*super_scale, raster20_ds.RasterCount)
    raster10_ds = raster10_driver.Create(raster10_path, xsize=raster10_shape[0], ysize=raster10_shape[1],
                                         bands=raster10_shape[2], eType=data_type)
    if not raster10_ds:
        print("Unable to create image {} with driver {}".format(raster10_path, format))
        sys.exit(1)

    raster10_geotransform = [raster20_geotransform[0], raster20_geotransform[1] / super_scale, raster20_geotransform[2],
                             raster20_geotransform[3], raster20_geotransform[4], raster20_geotransform[5] / super_scale]
    raster10_ds.SetGeoTransform(raster10_geotransform)
    raster10_ds.SetProjection(raster20_proj)

    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    raster10_ds.WriteRaster(0, 0, raster10_shape[0], raster10_shape[1], raster10_array.tobytes())

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    raster10_ds.FlushCache()
    del raster10_ds
    del raster20_ds

    print("### Success @ nn_supres_20_10() ##################")


def main():
    print("######################################################################################")
    print("### Resolution extractor from Sentinel-2 L2A image (in .xml) #########################")
    print("######################################################################################")

    ###########################################################
    # cmd line
    opts = parse_args()
    raster20_path = opts.src_path
    raster10_path = opts.target_path
    res_scale = int(opts.res_scale)

    # raster20_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c_fmask_mask_band\L1C_T31TFN_20190103T104708_Fmask4_mask.tif'
    # raster10_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c_fmask_mask_band_10m\L1C_T31TFN_20190103T104708_Fmask4_mask.tif'
    # res_scale = 2

    ###########################################################
    nn_supres_20_10(raster20_path, raster10_path, res_scale)

    ###########################################################
    # close
    print("### Task over #############################################")


if __name__ == "__main__":
    main()
