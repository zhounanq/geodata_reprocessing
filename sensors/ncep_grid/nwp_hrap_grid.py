# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import datetime
import argparse
import math
import numpy as np
from osgeo import gdal, osr


def parse_args():
    parser = argparse.ArgumentParser(description='***')
    # parser.add_argument('--src-file', required=False, type=str, default="./",
    #                     help='source HDF5 file for band extracting')
    # parser.add_argument('--target-file', required=False, type=str, default="./data",
    #                     help='target file for writing results')
    # parser.add_argument('--georef-file', required=False, type=str, default="./data/data.tif",
    #                     help='spatial reference for results')
    opts = parser.parse_args()
    return opts


def lonlat2hrap(lon, lat):
    def deg2rad(deg):
        return deg * (math.pi / 180)

    stlat = 60.0
    clon = 15.0
    rad = 6371.2

    sfactor = (1+math.sin(deg2rad(stlat))) / (1+math.sin(deg2rad(lat)))
    R = rad * math.cos(deg2rad(lat)) * sfactor
    x = R * math.cos(deg2rad(lon+clon))
    y = R * math.sin(deg2rad(lon+clon))

    hrapx = x / 4.7625 + 401
    hrapy = y / 4.7625 + 1601

    return [hrapx, hrapy]


def transform_grib_tiff(src_grib, target_tiff):
    """
    Transform [NCEP/EMC U.S. Stage IV imagery [NCAR/EOL]] to Tiff image.
    :param src_grib:
    :param target_tiff:
    :return:
    """
    # Open grib dataset
    grid_ds = gdal.Open(src_grib)
    if grid_ds is None:
        print("Wrong: to open dataset")
        return False
    # here can print info about grib data

    # Create driver for tiff
    tiff_driver = gdal.GetDriverByName('GTiff')
    tiff_ds = tiff_driver.CreateCopy(target_tiff, grid_ds, 0)

    # Properly close dataset to flush to disk
    tiff_ds = None
    grid_ds = None
    print("### [transform_grib_tiff] over!")


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### ***            ########################################")
    print("### ", now)
    print("###########################################################")

    # console parameters
    opts = parse_args()

    # test parameters
    grib_file = "G:/FF/application_dataset/AmericanWatershed/Precipitation NCEPEMC 4KM Gridded Data (GRIB) Stage IV Data/ST4.2015030112.24h"
    # grib_file = "G:/FF/application_dataset/AmericanWatershed/Precipitation NCEPEMC 4KM Gridded Data (GRIB) Stage IV Data/st4_conus.2021020112.24h.grb2"

    target_tiff = "./data/tif-proj.tif"

    transform_grib_tiff(grib_file, target_tiff)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
