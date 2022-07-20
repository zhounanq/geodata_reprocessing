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


def parse_args():
    parser = argparse.ArgumentParser(description='Sentinel-2 L2A image (in .xml)')
    parser.add_argument('--src-path', required=False, type=str,
                        default="./data/random.xml",
                        help='source (input) raster file in HDF format')
    parser.add_argument('--target-path', required=False, type=str,
                        default="./data/target.tif",
                        help='target raster file in TIFF format')
    parser.add_argument('--res', required=False, type=str,
                        default="10m",
                        help='target resolution in [10m, 20m, slc]')
    opts = parser.parse_args()
    return opts


def read_s2image_info(s2img_path):
    """

    :param s2img_path:
    :return:
    """
    s2_dataset = gdal.Open(s2img_path, gdal.GA_ReadOnly)
    if not s2_dataset:
        print('Unable to open %s' % s2img_path)
        sys.exit(1)
    print("Driver: {}/{}".format(s2_dataset.GetDriver().ShortName, s2_dataset.GetDriver().LongName))

    s2ds_list = s2_dataset.GetSubDatasets()
    if len(s2ds_list) != 4:
        print('Maybe %s not a Sentinel2 image' % s2img_path)
        sys.exit(1)

    for subinfo in s2ds_list:
        print('Sub image from Sentinel-2 image, with {}'.format(subinfo[1]))
        s2ds_sub = gdal.Open(subinfo[0])
        if not s2ds_sub:
            print('Unable to open sub image %s' % subinfo[0])
            sys.exit(1)

        print("Size is {} x {} x {}".format(s2ds_sub.RasterXSize, s2ds_sub.RasterYSize, s2ds_sub.RasterCount))
        print("Projection is {}".format(s2ds_sub.GetProjection()))
        sub_geotransform = s2ds_sub.GetGeoTransform()
        if sub_geotransform:
            print("Origin = ({}, {})".format(sub_geotransform[0], sub_geotransform[3]))
            print("Pixel Size = ({}, {})".format(sub_geotransform[1], sub_geotransform[5]))
        print("Band Type={}".format(gdal.GetDataTypeName(s2ds_sub.GetRasterBand(1).DataType)))
        print("Band Scale={}".format(s2ds_sub.GetRasterBand(1).GetScale()))
        print("Band Offset={}".format(s2ds_sub.GetRasterBand(1).GetOffset()))

        sub1_metadata = s2ds_sub.GetMetadata()

        del s2ds_sub
    # for

    return s2ds_list


def resolution_extract_10m(s2img_path, target_path, format='GTiff'):
    """

    """

    #################################################################
    # 0. open sentinel-2 images
    s2_dataset = gdal.Open(s2img_path, gdal.GA_ReadOnly)
    if not s2_dataset:
        print('Unable to open %s' % s2img_path)
        sys.exit(1)
    print("Driver: {}/{}".format(s2_dataset.GetDriver().ShortName, s2_dataset.GetDriver().LongName))

    s2ds_list = s2_dataset.GetSubDatasets()
    if len(s2ds_list) != 4:
        print('Maybe %s not a Sentinel2 image' % s2img_path)
        sys.exit(1)

    # 1. open sub1 dataset
    s2ds_sub1 = gdal.Open(s2ds_list[0][0])
    if not s2ds_sub1:
        print('Unable to open sub image {}'.format(s2ds_list[0][0]))
        sys.exit(1)

    print('Sub image from Sentinel-2 image, with {}'.format(s2ds_list[0][1]))
    print("Size is {} x {} x {}".format(s2ds_sub1.RasterXSize, s2ds_sub1.RasterYSize, s2ds_sub1.RasterCount))
    print("Projection is {}".format(s2ds_sub1.GetProjection()))
    print("Band Type={}".format(gdal.GetDataTypeName(s2ds_sub1.GetRasterBand(1).DataType)))

    sub1_geotransform = s2ds_sub1.GetGeoTransform()
    if sub1_geotransform:
        print("Origin = ({}, {})".format(sub1_geotransform[0], sub1_geotransform[3]))
        print("Pixel Size = ({}, {})".format(sub1_geotransform[1], sub1_geotransform[5]))

    sub1_metadata = s2ds_sub1.GetMetadata()
    if sub1_metadata:
        print('Meta data={}'.format(sub1_metadata))
        print('BOA_QUANTIFICATION_VALUE={}'.format(sub1_metadata['BOA_QUANTIFICATION_VALUE']))

    #################################################################
    # 2. get the special band and read data
    # [B4,B3,B2,B8]
    data_type = s2ds_sub1.GetRasterBand(1).DataType
    img_shape = (s2ds_sub1.RasterXSize, s2ds_sub1.RasterYSize, s2ds_sub1.RasterCount)

    r_band = s2ds_sub1.GetRasterBand(1)
    g_band = s2ds_sub1.GetRasterBand(2)
    b_band = s2ds_sub1.GetRasterBand(3)
    nir_band = s2ds_sub1.GetRasterBand(4)

    red_array = r_band.ReadAsArray(xoff=0, yoff=0, win_xsize=r_band.XSize, win_ysize=r_band.YSize,
                                   buf_xsize=r_band.XSize, buf_ysize=r_band.YSize, buf_type=data_type)
    green_array = g_band.ReadAsArray(xoff=0, yoff=0, win_xsize=r_band.XSize, win_ysize=r_band.YSize,
                                     buf_xsize=r_band.XSize, buf_ysize=r_band.YSize, buf_type=data_type)
    blue_array = b_band.ReadAsArray(xoff=0, yoff=0, win_xsize=r_band.XSize, win_ysize=r_band.YSize,
                                    buf_xsize=r_band.XSize, buf_ysize=r_band.YSize, buf_type=data_type)
    nir_array = nir_band.ReadAsArray(xoff=0, yoff=0, win_xsize=nir_band.XSize, win_ysize=nir_band.YSize,
                                     buf_xsize=nir_band.XSize, buf_ysize=nir_band.YSize, buf_type=data_type)

    #################################################################
    # 3. write image
    target_driver = gdal.GetDriverByName(format)
    metadata = target_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(format))

    dst_ds = target_driver.Create(target_path, xsize=img_shape[0], ysize=img_shape[1], bands=img_shape[2], eType=data_type)
    if not dst_ds:
        print("Unable to create image {} with driver {}".format(target_path, format))
        sys.exit(1)
    dst_ds.SetProjection(s2ds_sub1.GetProjection())
    dst_ds.SetGeoTransform(s2ds_sub1.GetGeoTransform())

    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    dst_ds.GetRasterBand(1).WriteRaster(0, 0, img_shape[0], img_shape[1], blue_array.tobytes())
    dst_ds.GetRasterBand(2).WriteRaster(0, 0, img_shape[0], img_shape[1], green_array.tobytes())
    dst_ds.GetRasterBand(3).WriteRaster(0, 0, img_shape[0], img_shape[1], red_array.tobytes())
    dst_ds.GetRasterBand(4).WriteRaster(0, 0, img_shape[0], img_shape[1], nir_array.tobytes())

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    dst_ds.FlushCache()
    del dst_ds
    del s2ds_sub1

    print("### Success @ resolution_extract_10m() ##################")


def resolution_extract_20m(s2img_path, target_path, format='GTiff'):
    """

    """

    #################################################################
    # 0. open sentinel-2 images
    s2_dataset = gdal.Open(s2img_path, gdal.GA_ReadOnly)
    if not s2_dataset:
        print('Unable to open %s' % s2img_path)
        sys.exit(1)
    print("Driver: {}/{}".format(s2_dataset.GetDriver().ShortName, s2_dataset.GetDriver().LongName))

    s2ds_list = s2_dataset.GetSubDatasets()
    if len(s2ds_list) != 4:
        print('Maybe %s not a Sentinel2 image' % s2img_path)
        sys.exit(1)

    # 1. open sub2 dataset
    s2ds_sub2 = gdal.Open(s2ds_list[1][0])
    if not s2ds_sub2:
        print('Unable to open sub image {}'.format(s2ds_list[1][0]))
        sys.exit(1)

    print('Sub image from Sentinel-2 image, with {}'.format(s2ds_list[1][1]))
    print("Size is {} x {} x {}".format(s2ds_sub2.RasterXSize, s2ds_sub2.RasterYSize, s2ds_sub2.RasterCount))
    print("Projection is {}".format(s2ds_sub2.GetProjection()))
    print("Band Type={}".format(gdal.GetDataTypeName(s2ds_sub2.GetRasterBand(1).DataType)))

    sub2_geotransform = s2ds_sub2.GetGeoTransform()
    if sub2_geotransform:
        print("Origin = ({}, {})".format(sub2_geotransform[0], sub2_geotransform[3]))
        print("Pixel Size = ({}, {})".format(sub2_geotransform[1], sub2_geotransform[5]))

    sub2_metadata = s2ds_sub2.GetMetadata()
    if sub2_metadata:
        print('Meta data={}'.format(sub2_metadata))
        print('BOA_QUANTIFICATION_VALUE={}'.format(sub2_metadata['BOA_QUANTIFICATION_VALUE']))

    #################################################################
    # 2. get the special band and read data
    # [B5,B6,B7,B8A,B11,B12,AOT,CLD,SCL]
    data_type = s2ds_sub2.GetRasterBand(1).DataType
    img_shape = (s2ds_sub2.RasterXSize, s2ds_sub2.RasterYSize, 6)

    b5_band = s2ds_sub2.GetRasterBand(1)
    b6_band = s2ds_sub2.GetRasterBand(2)
    b7_band = s2ds_sub2.GetRasterBand(3)
    b8a_band = s2ds_sub2.GetRasterBand(4)
    b11_band = s2ds_sub2.GetRasterBand(5)
    b12_band = s2ds_sub2.GetRasterBand(6)

    b5_array = b5_band.ReadAsArray(xoff=0, yoff=0, win_xsize=b5_band.XSize, win_ysize=b5_band.YSize,
                                   buf_xsize=b5_band.XSize, buf_ysize=b5_band.YSize, buf_type=data_type)
    b6_array = b6_band.ReadAsArray(xoff=0, yoff=0, win_xsize=b6_band.XSize, win_ysize=b6_band.YSize,
                                     buf_xsize=b6_band.XSize, buf_ysize=b6_band.YSize, buf_type=data_type)
    b7_array = b7_band.ReadAsArray(xoff=0, yoff=0, win_xsize=b7_band.XSize, win_ysize=b7_band.YSize,
                                    buf_xsize=b7_band.XSize, buf_ysize=b7_band.YSize, buf_type=data_type)
    b8a_array = b8a_band.ReadAsArray(xoff=0, yoff=0, win_xsize=b8a_band.XSize, win_ysize=b8a_band.YSize,
                                     buf_xsize=b8a_band.XSize, buf_ysize=b8a_band.YSize, buf_type=data_type)
    b11_array = b11_band.ReadAsArray(xoff=0, yoff=0, win_xsize=b11_band.XSize, win_ysize=b11_band.YSize,
                                     buf_xsize=b11_band.XSize, buf_ysize=b11_band.YSize, buf_type=data_type)
    b12_array = b12_band.ReadAsArray(xoff=0, yoff=0, win_xsize=b12_band.XSize, win_ysize=b12_band.YSize,
                                     buf_xsize=b12_band.XSize, buf_ysize=b12_band.YSize, buf_type=data_type)

    #################################################################
    # 3. write image
    target_driver = gdal.GetDriverByName(format)
    metadata = target_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(format))

    dst_ds = target_driver.Create(target_path, xsize=img_shape[0], ysize=img_shape[1], bands=img_shape[2], eType=data_type)
    if not dst_ds:
        print("Unable to create image {} with driver {}".format(target_path, format))
        sys.exit(1)
    dst_ds.SetProjection(s2ds_sub2.GetProjection())
    dst_ds.SetGeoTransform(s2ds_sub2.GetGeoTransform())
    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    dst_ds.GetRasterBand(1).WriteRaster(0, 0, img_shape[0], img_shape[1], b5_array.tobytes())
    dst_ds.GetRasterBand(2).WriteRaster(0, 0, img_shape[0], img_shape[1], b6_array.tobytes())
    dst_ds.GetRasterBand(3).WriteRaster(0, 0, img_shape[0], img_shape[1], b7_array.tobytes())
    dst_ds.GetRasterBand(4).WriteRaster(0, 0, img_shape[0], img_shape[1], b8a_array.tobytes())
    dst_ds.GetRasterBand(5).WriteRaster(0, 0, img_shape[0], img_shape[1], b11_array.tobytes())
    dst_ds.GetRasterBand(6).WriteRaster(0, 0, img_shape[0], img_shape[1], b12_array.tobytes())

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    dst_ds.FlushCache()
    del dst_ds
    del s2ds_sub2

    print("### Success @ resolution_extract_20m() ##################")


def resolution_extract_aot_cld_slc(s2img_path, target_path, format='GTiff'):
    """

    """

    #################################################################
    # 0. open sentinel-2 images
    s2_dataset = gdal.Open(s2img_path, gdal.GA_ReadOnly)
    if not s2_dataset:
        print('Unable to open %s' % s2img_path)
        sys.exit(1)
    print("Driver: {}/{}".format(s2_dataset.GetDriver().ShortName, s2_dataset.GetDriver().LongName))

    s2ds_list = s2_dataset.GetSubDatasets()
    if len(s2ds_list) != 4:
        print('Maybe %s not a Sentinel2 image' % s2img_path)
        sys.exit(1)

    # 1. open sub2 dataset
    s2ds_sub2 = gdal.Open(s2ds_list[1][0])
    if not s2ds_sub2:
        print('Unable to open sub image {}'.format(s2ds_list[1][0]))
        sys.exit(1)

    data_type = s2ds_sub2.GetRasterBand(1).DataType
    img_shape = (s2ds_sub2.RasterXSize, s2ds_sub2.RasterYSize, s2ds_sub2.RasterCount)

    print('Sub image from Sentinel-2 image, with {}'.format(s2ds_list[1][1]))
    print("Size is {} x {} x {}".format(s2ds_sub2.RasterXSize, s2ds_sub2.RasterYSize, s2ds_sub2.RasterCount))
    print("Projection is {}".format(s2ds_sub2.GetProjection()))
    print("Band Type={}".format(gdal.GetDataTypeName(s2ds_sub2.GetRasterBand(1).DataType)))

    sub2_geotransform = s2ds_sub2.GetGeoTransform()
    if sub2_geotransform:
        print("Origin = ({}, {})".format(sub2_geotransform[0], sub2_geotransform[3]))
        print("Pixel Size = ({}, {})".format(sub2_geotransform[1], sub2_geotransform[5]))

    sub2_metadata = s2ds_sub2.GetMetadata()
    if sub2_metadata:
        print('Meta data={}'.format(sub2_metadata))
        print('BOA_QUANTIFICATION_VALUE={}'.format(sub2_metadata['BOA_QUANTIFICATION_VALUE']))

    #################################################################
    # 2. get the special band and read data
    # [B5,B6,B7,B8A,B11,B12,AOT,CLD,SCL]
    data_type = s2ds_sub2.GetRasterBand(1).DataType
    img_shape = (s2ds_sub2.RasterXSize, s2ds_sub2.RasterYSize, 3)

    aot_band = s2ds_sub2.GetRasterBand(7)
    cld_band = s2ds_sub2.GetRasterBand(8)
    slc_band = s2ds_sub2.GetRasterBand(9)

    aot_array = aot_band.ReadAsArray(xoff=0, yoff=0, win_xsize=aot_band.XSize, win_ysize=aot_band.YSize,
                                   buf_xsize=aot_band.XSize, buf_ysize=aot_band.YSize, buf_type=data_type)
    cld_array = cld_band.ReadAsArray(xoff=0, yoff=0, win_xsize=cld_band.XSize, win_ysize=cld_band.YSize,
                                     buf_xsize=cld_band.XSize, buf_ysize=cld_band.YSize, buf_type=data_type)
    slc_array = slc_band.ReadAsArray(xoff=0, yoff=0, win_xsize=slc_band.XSize, win_ysize=slc_band.YSize,
                                    buf_xsize=slc_band.XSize, buf_ysize=slc_band.YSize, buf_type=data_type)

    #################################################################
    # 3. write image
    target_driver = gdal.GetDriverByName(format)
    metadata = target_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(format))

    dst_ds = target_driver.Create(target_path, xsize=img_shape[0], ysize=img_shape[1], bands=img_shape[2], eType=data_type)
    if not dst_ds:
        print("Unable to create image {} with driver {}".format(target_path, format))
        sys.exit(1)
    dst_ds.SetProjection(s2ds_sub2.GetProjection())
    dst_ds.SetGeoTransform(s2ds_sub2.GetGeoTransform())
    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    dst_ds.GetRasterBand(1).WriteRaster(0, 0, img_shape[0], img_shape[1], aot_array.tobytes())
    dst_ds.GetRasterBand(2).WriteRaster(0, 0, img_shape[0], img_shape[1], cld_array.tobytes())
    dst_ds.GetRasterBand(3).WriteRaster(0, 0, img_shape[0], img_shape[1], slc_array.tobytes())

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    dst_ds.FlushCache()
    del dst_ds
    del s2ds_sub2

    print("### Success @ resolution_extract_slc() ##################")


def main():
    print("######################################################################################")
    print("### Resolution extractor from Sentinel-2 L2A image (in .xml) #########################")
    print("######################################################################################")
    hide_info = False

    beg_date = time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
    if not hide_info:
        print('### TIME: {}'.format(beg_date))

    ###########################################################
    # cmd line
    # opts = parse_args()
    # s2img_path = opts.src_path
    # s2res_path = opts.target_path
    # res = opts.res

    s2img_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c\S2A_MSIL2A_20190821T104031_N9999_R008_T31TFN_20220718T071759.SAFE\MTD_MSIL2A.xml'
    s2res_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c\S2A_MSIL2A_20190821_R008_T31TFN_20m.tif'
    res = '20m'

    ###########################################################
    # # 1. read gdal image using sentinel-2 driver.
    # s2ds_list = read_s2image_info(s2img_path)

    # 2. calculate index band.
    if res=='10m':
        resolution_extract_10m(s2img_path, s2res_path)
    elif res=='20m':
        resolution_extract_20m(s2img_path, s2res_path)
    elif res=='slc':
        resolution_extract_aot_cld_slc(s2img_path, s2res_path)
    else:
        print('Mode {} not supported'.format(res))

    ###########################################################
    # close
    end_date = time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
    if not hide_info:
        print('### TIME: {}'.format(end_date))
    print("### Task over #############################################")


if __name__ == "__main__":
    main()
