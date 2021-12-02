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


def raster_band_extractor(src_raster, target_raster, band_list=[1], file_format='GTiff'):

    data_type = None

    # reading src raster
    src_ds = gdal.Open(src_raster, gdal.GA_ReadOnly)
    if src_ds:
        print("Driver: {}/{}".format(src_ds.GetDriver().ShortName, src_ds.GetDriver().LongName))
        print("Size is {} x {} x {}".format(src_ds.RasterXSize, src_ds.RasterYSize, src_ds.RasterCount))

        print("Projection is {}".format(src_ds.GetProjection()))
        geotransform = src_ds.GetGeoTransform()
        if geotransform:
            print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
            print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

        raster_band0 = src_ds.GetRasterBand(1)
        if raster_band0:
            data_type = raster_band0.DataType
            print("Band Type = {}".format(gdal.GetDataTypeName(data_type)))
    else:
        raise Exception("Wrong source raster @{}".format(src_raster))
    # if

    # writing target raster
    target_band = len(band_list)
    src_wid, src_hei = src_ds.RasterXSize, src_ds.RasterYSize

    file_driver = gdal.GetDriverByName(file_format)
    metadata = file_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(file_format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(file_format))

    target_ds = file_driver.Create(target_raster, xsize=src_wid, ysize=src_hei, bands=target_band, eType=data_type)
    target_ds.SetProjection(src_ds.GetProjection())
    target_ds.SetGeoTransform(src_ds.GetGeoTransform())
    if not target_ds:
        raise Exception("Wrong target raster @{}".format(target_raster))

    for idx, channel in enumerate(band_list):
        band_array = src_ds.GetRasterBand(channel + 1).ReadAsArray()
        target_ds.GetRasterBand(idx + 1).WriteArray(band_array)

    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    target_ds.FlushCache()


def main():
    print("#############################################################")

    img_path4 = "G:/FF/application_dataset/PROBAV_S10_TOC_X21Y08/PROBAV_S10_TOC_X21Y08_1KM.HDF5.tif"
    img_path2 = "G:/FF/application_dataset/PROBAV_S10_TOC_X21Y08/shp/csv/PROBAV_S10_TOC_X21Y08_1KM_YIGE.tif"
    pvcsv_path = "G:/FF/application_dataset/PROBAV_S10_TOC_X21Y08/shp/csv/pixel_tsattri_2020_yige.csv"


if __name__ == "__main__":
    main()
