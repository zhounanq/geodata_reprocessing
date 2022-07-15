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

    img_path4 = r'F:\application_dataset\datafusion\S2A_MSIL2A_20220411_R061_T48RWU_10m.tif'
    img_path2 = r'F:\application_dataset\datafusion\L1C_T31TFN_20190418_Fmask4_mask_10m.tif'

    copy_spatialref(img_path4, img_path2)


    print("### Task over #############################################")


if __name__ == "__main__":
    main()
