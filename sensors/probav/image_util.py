# -*- coding: utf-8 -*-

"""
Image operations

Author: Zhou Ya'nan
"""
import os
import time
import datetime
import argparse
import gc
import numpy as np
import pandas as pd

from osgeo import gdal, osr


def list_datasets(path, ext):
    """
    List the data sets in a folder
    """
    datsets_ls = []
    for f in os.listdir(path):
        if os.path.splitext(f)[1][1:] == ext:
            datsets_ls.append(f)
    return datsets_ls


def load_gdalimage_array(image_array):
    pass


def load_gdalimage(image_path):
    """Load image on disk, with gdal driver.

    Parameters
    ----------
    image_path : string
        The path of image.

    :return : np.array
    """
    data_type = None

    image_ds = gdal.Open(image_path, gdal.GA_ReadOnly)
    if not image_ds:
        print("Fail to open image {}".format(image_path))
        return None
    else:
        print("Driver: {}/{}".format(image_ds.GetDriver().ShortName, image_ds.GetDriver().LongName))
        print("Size is {} x {} x {}".format(image_ds.RasterXSize, image_ds.RasterYSize, image_ds.RasterCount))

        print("Projection is {}".format(image_ds.GetProjection()))
        geotransform = image_ds.GetGeoTransform()
        if geotransform:
            print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
            print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

        raster_band0 = image_ds.GetRasterBand(1)
        if raster_band0:
            data_type = raster_band0.DataType
            print("Band Type = {}".format(gdal.GetDataTypeName(data_type)))

            min = raster_band0.GetMinimum()
            max = raster_band0.GetMaximum()
            if not min or not max:
                (min, max) = raster_band0.ComputeRasterMinMax(True)
            print("Min = {:.3f}, Max = {:.3f}".format(min, max))

            if raster_band0.GetOverviewCount() > 0:
                print("Band has {} overviews".format(raster_band0.GetOverviewCount()))
            if raster_band0.GetRasterColorTable():
                print("Band has a color table with {} entries".format(raster_band0.GetRasterColorTable().GetCount()))

    image_shape = (image_ds.RasterYSize, image_ds.RasterXSize, image_ds.RasterCount)
    # image_array = np.zeros(image_shape, dtype=None)
    image_array = image_ds.ReadAsArray(xoff=0, yoff=0, xsize=image_shape[1], ysize=image_shape[0],
                                       buf_xsize=image_shape[1], buf_ysize=image_shape[0],
                                       buf_type=data_type)
    if len(image_array.shape) == 2:
        image_array = image_array[:,:,np.newaxis]

    return image_array


def saveas_gdalimage(img_array, save_path, format='GTiff'):
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

    dst_ds = file_driver.Create(save_path, xsize=img_shape[1], ysize=img_shape[0], bands=img_shape[2],
                                eType=gdal.GDT_Float32)
    if not dst_ds:
        print("Fail to create image {}".format(save_path))
        return False

    # raster = np.zeros((img_shape[1], img_shape[0]), dtype=np.float32)
    for channel in range(0, img_shape[2]):
        print("### Writing band {}".format(channel))
        channel_array = img_array[:, :, channel:channel + 1]
        channel_array = channel_array.reshape(img_shape[0], img_shape[1])
        channel_array = channel_array.astype(np.float32)

        # dst_ds.GetRasterBand(channel + 1).WriteArray(channel_array)
        dst_ds.GetRasterBand(channel + 1).WriteRaster(0, 0, img_shape[1], img_shape[0], channel_array.tostring())
        # if (channel+1) % 16 == 0: gc.collect()

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


def overwrite_pixelvalues(img_path4, img_path2, pvcsv_path, band_index=0):
    img4_array = load_gdalimage(img_path4)
    img4_array = img4_array.transpose(2, 0, 1)
    img4_array = img4_array.astype(float)

    band4_array = img4_array[band_index]
    band2_array = np.zeros_like(band4_array)

    csv_pd = pd.read_csv(pvcsv_path, header=None)
    csv_pd = csv_pd.fillna(0)
    for index, row in csv_pd.iterrows():
        xx, yy, vv = int(row[0]), int(row[1]), row[2]
        band2_array[yy - 1][xx - 1] = vv

    # with open(pvcsv_path) as pvscv_f:
    #     csv_data = np.loadtxt(pvscv_f, delimiter=",")
    #     for pp in range(0, csv_data.shape[0]):
    #         xx, yy, vv = int(csv_data[pp][0]), int(csv_data[pp][1]), csv_data[pp][2]
    #         band2_array[yy-1][xx-1] = vv

    img4_array[band_index] = band2_array
    img4_array = img4_array.transpose(1, 2, 0)
    ret = saveas_gdalimage(img4_array, img_path2)
    ret = copy_spatialref(img_path4, img_path2)

    return True


def main():
    print("### image_util.main() ###########################################")

    img_path4 = "G:/FF/application_dataset/PROBAV_S10_TOC_X21Y08/PROBAV_S10_TOC_X21Y08_1KM.HDF5.tif"
    img_path2 = "G:/FF/application_dataset/PROBAV_S10_TOC_X21Y08/shp/csv/PROBAV_S10_TOC_X21Y08_1KM_YIGE.tif"
    pvcsv_path = "G:/FF/application_dataset/PROBAV_S10_TOC_X21Y08/shp/csv/pixel_tsattri_2020_yige.csv"

    overwrite_pixelvalues(img_path4, img_path2, pvcsv_path)


if __name__ == "__main__":
    main()
