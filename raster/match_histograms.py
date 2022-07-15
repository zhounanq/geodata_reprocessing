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
from skimage import exposure
from osgeo import gdal, osr

os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
gdal.UseExceptions()


def hist_match(src_path, ref_path, matched_path, format='GTiff'):

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

    ref_ds = gdal.Open(ref_path, gdal.GA_ReadOnly)
    if not ref_ds:
        print('Unable to open image {}'.format(ref_path))
        sys.exit(1)
    ref_shape = (ref_ds.RasterXSize, ref_ds.RasterYSize, ref_ds.RasterCount)

    #################################################################
    # 2. get data
    src_array = src_ds.ReadAsArray()
    ref_array = ref_ds.ReadAsArray()

    multi = 2 if src_shape[-1] > 1 else None
    matched_array = exposure.match_histograms(src_array, ref_array, channel_axis=multi)

    #################################################################
    # 3. write image
    matched_driver = gdal.GetDriverByName(format)
    matched_ds = matched_driver.Create(matched_path, xsize=src_shape[0], ysize=src_shape[1], bands=src_shape[2], eType=src_datatype)
    if not matched_ds:
        print("Unable to create image {} with driver {}".format(matched_path, format))
        sys.exit(1)
    matched_ds.SetGeoTransform(src_geotransform)
    matched_ds.SetProjection(src_proj)

    matched_ds.WriteRaster(0, 0, src_shape[0], src_shape[1], matched_array.tobytes())

    #################################################################
    # 4. close
    # print("### Building overviews")
    # dst_ds.BuildOverviews("NEAREST")
    matched_ds.FlushCache()
    del matched_ds, ref_array, src_array

    print("### Success @ hist_match() ##################")


def main():
    print("######################################################################################")
    print("### Resolution extractor from Sentinel-2 L2A image (in .xml) #########################")
    print("######################################################################################")

    src_path = r'F:\application_dataset\datafusion\tongnan\S2A_MSIL2A_20220421_R061_T48RWU_10m_p.tif'
    ref_path = r'F:\application_dataset\datafusion\tongnan\S2A_MSIL2A_20220421_R061_T48RWU_10m.tif'
    matched_path = r'F:\application_dataset\datafusion\tongnan\S2A_MSIL2A_20220421_R061_T48RWU_10m_p_match.tif'

    hist_match(src_path, ref_path, matched_path)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
