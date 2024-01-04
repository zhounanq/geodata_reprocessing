# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import datetime
import argparse
import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC
from osgeo import gdal, osr
gdal.UseExceptions()


def parse_args():
    parser = argparse.ArgumentParser(description='AOD extraction from MCD19A2')
    parser.add_argument('--src-hdf', required=False, type=str,
                        default="./data/random.hdf",
                        help='source (input) raster file in HDF format')
    parser.add_argument('--target-raster', required=False, type=str,
                        default="./data/target.tif",
                        help='target raster file in TIFF format')
    opts = parser.parse_args()
    return opts


def aod_read_mvc(hdf_path, aod_key = 'Optical_Depth_055'):
    """

    """
    print("### Reading HDF image {}".format(hdf_path))

    hdf_scidata = SD(hdf_path, SDC.READ)
    # print (hdf_scidata.info(), hdf_scidata.attributes())

    scidata_dict = hdf_scidata.datasets()
    for idx, sds in enumerate(scidata_dict.keys()):
        print (idx, sds)

    aod_dataset = hdf_scidata.select(aod_key)
    print(aod_dataset.attributes(), aod_dataset.info())

    attrs = aod_dataset.attributes(full=1)
    fill_value = attrs['_FillValue'][0]
    scale_factor = attrs['scale_factor'][0]

    aod_data = aod_dataset.get()

    aod_data = aod_data.astype('float32')
    aod_data[aod_data == fill_value] = np.nan
    # aod_mvc = np.nanmean(aod_data, axis=0)
    aod_mvc = np.nanmax(aod_data, axis=0)
    aod_mvc[np.isnan(aod_mvc)] = fill_value
    aod_mean = aod_mvc.astype('int16')

    return aod_mean # shape (channel, xsize, ysize)


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

    type_dict = {'uint8': gdal.GDT_Byte, 'uint16': gdal.GDT_UInt16, 'uint32': gdal.GDT_UInt32,
                 'int16': gdal.GDT_Int16, 'int32': gdal.GDT_Int32,
                 'float16': gdal.GDT_Float32, 'float32': gdal.GDT_Float32, 'float64': gdal.GDT_Float32}
    gdal_type = type_dict[img_array.dtype.name]

    file_format = format
    file_driver = gdal.GetDriverByName(file_format)
    metadata = file_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(file_format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(file_format))

    img_shape = img_array.shape
    dst_ds = file_driver.Create(save_path, xsize=img_shape[1], ysize=img_shape[0], bands=1, eType=gdal.GDT_Float32)
    if not dst_ds:
        print("Fail to create image {}".format(save_path))
        return False
    dst_ds.GetRasterBand(1).WriteArray(img_array)

    dst_ds.GetRasterBand(1).SetNoDataValue(-28672)

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


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### ***            ########################################")
    print("### ", now)
    print("###########################################################")

    # cmd line
    opts = parse_args()
    hdf_path = opts.src_hdf
    save_path = opts.target_raster
    spatial_ref_path = ''

    # for test
    # hdf_path = r'F:\application_dataset\CovidVegGreen\MCD19A2\2017\MCD19A2.A2017001.h27v05.006.2018114111739.hdf'
    # save_path = r'F:\application_dataset\CovidVegGreen\MCD19A2\2017\aod055\MCD19A2.A2017001_AOD055.mvc.tif'
    spatial_ref_path = r'F:\application_dataset\CovidVegGreen\MCD19A2\2017\aod055\spatialref.tif'

    aod_mvc_array = aod_read_mvc(hdf_path)
    save_band_image(aod_mvc_array, save_path)
    copy_spatialref(spatial_ref_path, save_path)


    print("### Task over #############################################")


if __name__ == "__main__":
    main()
