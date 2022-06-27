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
import cv2
from scipy import signal
from osgeo import gdal, osr
gdal.UseExceptions()


def gauss_blur(band_array, ksize=(3,3), sigmaX=0, sigmaY=0, _boundary = 'fill', _fillvalue=0):

    array_shape = band_array.shape

    # @param ksize Aperture size. It should be odd ( \f$\texttt{ksize} \mod 2 = 1\f$ ) and positive.
    # @param sigma Gaussian standard deviation. If it is non-positive, it is computed from ksize as
    # `sigma = 0.3*((ksize-1)*0.5 - 1) + 0.8`.
    gaussKernel_x = cv2.getGaussianKernel(ksize[0], sigmaX, cv2.CV_64F)
    gaussKernel_x = np.transpose(gaussKernel_x)
    gaussKernel_y = cv2.getGaussianKernel(ksize[1], sigmaY, cv2.CV_64F)

    # 图像矩阵与水平高斯卷积核卷积
    gaussBlur_x = signal.convolve2d(band_array, gaussKernel_x, mode='same', boundary=_boundary, fillvalue=_fillvalue)
    # 与垂直方向上的高斯卷积核卷积
    gaussBlur_xy = signal.convolve2d(gaussBlur_x, gaussKernel_y, mode='same', boundary=_boundary, fillvalue=_fillvalue)

    gaussBlur_xy = gaussBlur_xy.astype(band_array.dtype)
    return gaussBlur_xy


def gauss_blur2(band_array, ksize=(3,3), sigmaX=0):
    #@param ksize Aperture size. It should be odd ( \f$\texttt{ksize} \mod 2 = 1\f$ ) and positive.
    #@param sigma Gaussian standard deviation. If it is non-positive, it is computed from ksize as
    # `sigma = 0.3*((ksize-1)*0.5 - 1) + 0.8`.
    gauss_array = cv2.GaussianBlur(band_array, ksize=ksize, sigmaX=sigmaX, borderType=cv2.BORDER_CONSTANT)

    gauss_array = gauss_array.astype(band_array.dtype)

    return gauss_array


def load_gdalimage_band(image_path, channel=0):
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
    band_array = image_ds.GetRasterBand(channel + 1).ReadAsArray()

    return band_array


def saveas_gdalimage(band_array, save_path, format='GTiff'):
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
    gdal_type = type_dict[band_array.dtype.name]

    file_format = format
    file_driver = gdal.GetDriverByName(file_format)
    metadata = file_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(file_format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(file_format))

    img_shape = band_array.shape
    dst_ds = file_driver.Create(save_path, xsize=img_shape[1], ysize=img_shape[0], bands=1, eType=gdal.GDT_Int16)
    if not dst_ds:
        print("Fail to create image {}".format(save_path))
        return False

    dst_ds.GetRasterBand(1).WriteArray(band_array)

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
    print("#############################################################")

    srcimg_path = r'F:\application_dataset\downscale\S2B_MSIL1C_20220517_gs11_d2.tif'
    gsbimg_path = r'F:\application_dataset\downscale\S2B_MSIL1C_20220517_gs11_d2_gs11.tif'
    difimg_path = r'F:\application_dataset\downscale\S2B_MSIL1C_20220517_gs11_d2_gs11_dif.tif'

    band_array = load_gdalimage_band(srcimg_path, channel=0)
    gauss_array = gauss_blur(band_array, ksize=(11,11), sigmaX=0, sigmaY=0)
    diff_array = band_array.astype(np.float32)-gauss_array.astype(np.float32)

    saveas_gdalimage(gauss_array, gsbimg_path)
    copy_spatialref(srcimg_path, gsbimg_path)

    saveas_gdalimage(diff_array, difimg_path)
    copy_spatialref(srcimg_path, difimg_path)

    print("### Task is over!")


if __name__ == "__main__":
    main()
