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
    parser = argparse.ArgumentParser(description='Super resolution using nearest neighbour scaling')
    parser.add_argument('--src-path', required=False, type=str,
                        default="./data/random.tif",
                        help='source (input) raster file in TIFF format')
    parser.add_argument('--target-path', required=False, type=str,
                        default="./data/target.tif",
                        help='target raster file in TIFF format')
    parser.add_argument('--datatype', required=False, type=str,
                        default="uint8",
                        help='datatype for results in [uint8,uint16,uint32,int16]')
    opts = parser.parse_args()
    return opts


def convert_raster_datatype(src_path, target_path, datatype='uint8', format='GTiff'):

    """

    """

    #################################################################
    # 1. open source data
    src_ds = gdal.Open(src_path, gdal.GA_ReadOnly)
    if not src_ds:
        print('Unable to open image {}'.format(src_path))
        sys.exit(1)

    src_proj = src_ds.GetProjection()
    src_geotransform = src_ds.GetGeoTransform()
    src_datatype = src_ds.GetRasterBand(1).DataType
    src_shape = (src_ds.RasterXSize, src_ds.RasterYSize, src_ds.RasterCount)

    #################################################################
    # 2. get data
    src_array = src_ds.ReadAsArray()

    gdal_type_dict = {'uint8': gdal.GDT_Byte, 'uint16': gdal.GDT_UInt16, 'uint32': gdal.GDT_UInt32,
                 'int16': gdal.GDT_Int16, 'int32': gdal.GDT_Int32,
                 'float32': gdal.GDT_Float32, 'float64': gdal.GDT_Float64}
    gdal_type = gdal_type_dict[datatype]

    np_type_dict = {'uint8': np.byte, 'uint16': np.uint16, 'uint32': np.uint32,
                    'int16': np.int16, 'int32': np.int32,
                    'float32': np.float32, 'float64': np.float64}
    tar_array = src_array.astype(np_type_dict[datatype])

    #################################################################
    # 3. write image
    tar_driver = gdal.GetDriverByName(format)
    tar_ds = tar_driver.Create(target_path, xsize=src_shape[0], ysize=src_shape[1], bands=src_shape[2], eType=gdal_type)
    if not tar_ds:
        print("Unable to create image {} with driver {}".format(target_path, format))
        sys.exit(1)

    tar_ds.SetGeoTransform(src_geotransform)
    tar_ds.SetProjection(src_proj)

    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    tar_ds.WriteRaster(0, 0, src_shape[0], src_shape[1], tar_array.tobytes())

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    src_ds.FlushCache()
    del src_ds, tar_ds

    print("### Success @ convert_raster_datatype() ##################")


def main():
    print("######################################################################################")
    print("### Resolution extractor from Sentinel-2 L2A image (in .xml) #########################")
    print("######################################################################################")

    ###########################################################
    # cmd line
    opts = parse_args()
    src_path = opts.src_path
    target_path = opts.target_path
    datatype = opts.datatype

    # src_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c_fmask_mask_band\L1C_T31TFN_20190103T104708_Fmask4_mask.tif'
    # target_path = r'H:\FF\application_dataset\2020-france-agri\s2_l1c_fmask_mask_band_10m\L1C_T31TFN_20190103T104708_Fmask4_mask.tif'
    # datatype = 'uint8'

    ###########################################################
    convert_raster_datatype(src_path, target_path, datatype)

    ###########################################################
    # close
    print("### Task over #############################################")


if __name__ == "__main__":
    main()
