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


def parse_args():
    parser = argparse.ArgumentParser(description='Band extractor for Raster dataset')
    parser.add_argument('--src-raster', required=False, type=str,
                        default="./data/random.tif",
                        help='source (input) raster file')
    parser.add_argument('--target-raster', required=False, type=str,
                        default="./data/target.tif",
                        help='target raster file')
    parser.add_argument('--band-list', required=False, type=str,
                        default=[0],
                        help='which bands to be extracted')
    opts = parser.parse_args()
    return opts


def raster_band_extractor(src_raster, target_raster, band_list=[0], file_format='GTiff'):
    """

    :param src_raster:
    :param target_raster:
    :param band_list:
    :param file_format:
    :return:
    """
    print("### Band extractor for []".format(src_raster))

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
    # target_ds.FlushCache()


def main():
    print("#############################################################")

    srcraster_list = [
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210205T033931_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210327T033531_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210426T033531_N0300_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210516T033541_N0300_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210725T033541_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210804T033541_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210824T033541_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20210923T033541_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2A_MSIL2A_20211003T033601_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210101T034139_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210111T034119_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210210T033859_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210220T033759_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210312T033539_N0214_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210421T033529_N0300_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210501T033529_N0300_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210531T033539_N0300_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210630T033539_N0300_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210720T033539_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210730T033539_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210809T033539_N0301_R061_T48RWU_ireci.tif',
        'i:\sentinel2-2021\L1C_T48RWU\index\ireci\S2B_MSIL2A_20210819T033539_N0301_R061_T48RWU_ireci.tif'
    ]

    for srcr in srcraster_list:
        targetr = srcr[:-4] + '_1.tif'
        raster_band_extractor(srcr, targetr)
        pass

    print("### Task is over!")


if __name__ == "__main__":
    main()
