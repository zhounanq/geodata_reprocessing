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
    parser = argparse.ArgumentParser(description='Masking raster image')
    parser.add_argument('--src-path', required=False, type=str,
                        default="./data/random.tif",
                        help='source (input) raster file in TIFF format')
    parser.add_argument('--target-path', required=False, type=str,
                        default="./data/target.tif",
                        help='target raster file in TIFF format')
    parser.add_argument('--mask-path', required=False, type=str,
                        default="./data/mask.tif",
                        help='mask raster file in TIFF format')
    opts = parser.parse_args()
    return opts


def pixel_wise_mask(src_path, target_path, mask_path, mask_mask_value=100, mask_value=0, format='GTiff'):
    """

    """

    #################################################################
    # 1. open source data
    source_ds = gdal.Open(src_path, gdal.GA_ReadOnly)
    if not source_ds:
        print('Unable to open image {}'.format(src_path))
        sys.exit(1)
    source_proj = source_ds.GetProjection()
    source_geotransform = source_ds.GetGeoTransform()
    data_type = source_ds.GetRasterBand(1).DataType
    source_shape = (source_ds.RasterXSize, source_ds.RasterYSize, source_ds.RasterCount)

    mask_ds = gdal.Open(mask_path, gdal.GA_ReadOnly)
    if not mask_ds:
        print('Unable to open image {}'.format(mask_path))
        sys.exit(1)
    mask_shape = (mask_ds.RasterXSize, mask_ds.RasterYSize, mask_ds.RasterCount)
    assert ((source_shape[0]==mask_shape[0]) and (source_shape[1]==mask_shape[1]))

    #################################################################
    # 2. create dataset
    target_driver = gdal.GetDriverByName(format)
    target_ds = target_driver.Create(target_path, xsize=source_shape[0], ysize=source_shape[1],
                                     bands=source_shape[2], eType=data_type)
    if not target_ds:
        print("Unable to create image {} with driver {}".format(target_path, format))
        sys.exit(1)

    target_ds.SetGeoTransform(source_geotransform)
    target_ds.SetProjection(source_proj)

    #################################################################
    # 3. write image
    mask_band_array = mask_ds.GetRasterBand(1).ReadAsArray()

    for bb in range(0, source_shape[2]):
        source_band_array = source_ds.GetRasterBand(bb+1).ReadAsArray()
        source_band_array[mask_band_array==mask_mask_value] = mask_value
        target_ds.GetRasterBand(bb + 1).WriteRaster(0, 0, source_shape[0], source_shape[1], source_band_array.tobytes())
        target_ds.GetRasterBand(bb + 1).SetNoDataValue(mask_value)
    # for

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    target_ds.FlushCache()
    del target_ds, mask_ds, source_ds

    print("### Success @ pixel_wise_mask() ##################")


def main():
    print("######################################################################################")
    print("### Resolution extractor from Sentinel-2 L2A image (in .xml) #########################")
    print("######################################################################################")

    ###########################################################
    # cmd line
    opts = parse_args()
    src_path = opts.src_path
    target_path = opts.target_path
    mask_path = opts.mask_path

    # src_path = r'H:\FF\application_dataset\2020-france-agri\s2_l2a_tif\10m\S2A_MSIL2A_20190103T104431_10m.tif'
    # target_path = r'H:\FF\application_dataset\2020-france-agri\s2_l2a_tif_mask\S2A_MSIL2A_20190103T104431_10m_mask.tif'
    # mask_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c_fmask_mask_band_10m\L1C_T31TFN_20190103T104708_Fmask4_mask_10m.tif'

    ###########################################################
    pixel_wise_mask(src_path, target_path, mask_path)


    ###########################################################
    # close
    print("### Task over #############################################")


if __name__ == "__main__":
    main()
