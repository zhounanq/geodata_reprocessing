# -*- coding: utf-8 -*-

"""
Functions for image operation in gdal

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import time
import datetime
import argparse
import gc
import numpy as np
from osgeo import gdal, osr
gdal.UseExceptions()


def save_band_image(img_array, save_path, format='GTiff'):
    """Save image on disk, with tiff format.

    Parameters
    ----------
    img_array : np.array,
        The image for saving (np.array).
    save_path :
        The path for output images.
        :param format:
    """
    print("### Writing image {}".format(save_path))
    img_shape = img_array.shape

    file_format = format
    file_driver = gdal.GetDriverByName(file_format)
    metadata = file_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(file_format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(file_format))

    dst_ds = file_driver.Create(save_path, xsize=img_shape[1], ysize=img_shape[0], bands=1, eType=gdal.GDT_Float32)
    if not dst_ds:
        print("Fail to create image {}".format(save_path))
        return False
    dst_ds.GetRasterBand(1).WriteArray(img_array)

    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    dst_ds.FlushCache()
    return True


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


