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
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


def parse_args_set_raster_nodata():
    parser = argparse.ArgumentParser(description='Setting nodata value for raster')
    parser.add_argument('--src_path', required=False, type=str,
                        default="./data/random.tif",
                        help='source (input) raster file in TIFF format')
    parser.add_argument('--nodata', required=False, type=int,
                        default=0,
                        help='no data for raster in INT format')
    opts = parser.parse_args()
    return opts


def copy_spatialref(img_path4, img_path2):
    image_ds4 = gdal.Open(img_path4, gdal.GA_ReadOnly)
    if not image_ds4:
        print("Fail to open image {}".format(img_path4))
        return False

    image_ds2 = gdal.Open(img_path2, gdal.GA_Update)
    if not image_ds2:
        print("Fail to open image {}".format(img_path2))
        return False

    proj = image_ds4.GetProjection()
    if proj:
        print("Projection is {}".format(proj))
    geotransform = image_ds4.GetGeoTransform()
    if geotransform:
        print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
        print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

    image_ds2.SetProjection(proj)
    image_ds2.SetGeoTransform(geotransform)

    print("### Copy spatial reference over")
    return True


def set_raster_nodata(raster_path, nodata=0):

    raster_ds = gdal.Open(raster_path, gdal.GA_Update)
    if not raster_ds:
        print("Fail to open image {}".format(raster_path))
        return False

    band_count = raster_ds.RasterCount
    for bb in range(0, band_count):
        raster_ds.GetRasterBand(bb+1).SetNoDataValue(nodata)

    raster_ds.FlushCache()
    del raster_ds

    print("### OVER @ set_raster_nodata()")


def main():
    print("######################################################################################")
    print("### Resolution extractor from Sentinel-2 L2A image (in .xml) #########################")
    print("######################################################################################")

    ###########################################################
    # cmd line

    # img_path4 = r'K:\FF\application_dataset\2021-yongchuan\4date\2021-01-01_2021-01-10\L1C_T48RWT_20210101_10m.tif'
    # img_path2 = r'K:\FF\application_dataset\2021-yongchuan\4date\2021-01-01_2021-01-10\L1C_T48RWT_20210103_10m.tif'
    # copy_spatialref(img_path4, img_path2)


    ###########################################################
    # cmd line
    opts = parse_args_set_raster_nodata()
    src_path = opts.src_path
    nodata = int(opts.nodata)

    src_path = r'K:\FF\application_dataset\2021-yongchuan\2mvc\L1C_T48RWT_2021051X_10m_yc.tif'
    nodata = 0

    set_raster_nodata(src_path, nodata)


    ###########################################################
    # cmd line


    print("### Task complete ! #############################################")


if __name__ == "__main__":
    main()
