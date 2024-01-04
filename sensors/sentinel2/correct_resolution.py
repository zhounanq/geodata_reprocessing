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
import numpy as np
from osgeo import gdal, osr
gdal.UseExceptions()


def correct_res(image_path, res_scale = 2):

    image_ds = gdal.Open(image_path, gdal.GA_Update)
    if not image_ds:
        print("Fail to open image {}".format(image_path))
        return False

    proj = image_ds.GetProjection()
    if proj:
        print("Projection is {}".format(proj))
    geotransform = image_ds.GetGeoTransform()
    if geotransform:
        print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
        print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

    correct_geotrans = [geotransform[0], geotransform[1] * res_scale, geotransform[2], geotransform[3], geotransform[4], geotransform[5] * res_scale]
    image_ds.SetGeoTransform(correct_geotrans)

    print("### OVER in [Correct resolution for image]")
    pass


def main():
    print("#############################################################")


    image_path2 = r'F:\application_dataset\datafusion\Sentinel2\S2B_MSIL1C_20220603T025549_N0400_R032_T50SME\S2B_MSIL1C_20220603T025549_N0400_R032_T50SME_20.tif'
    correct_res(image_path2, res_scale = 2)

    image_path6 = r'F:\application_dataset\datafusion\Sentinel2\S2B_MSIL1C_20220603T025549_N0400_R032_T50SME\S2B_MSIL1C_20220603T025549_N0400_R032_T50SME_60.tif'
    correct_res(image_path6, res_scale = 6)


    print("### Task is over!")


if __name__ == "__main__":
    main()
