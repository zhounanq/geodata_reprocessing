# -*- coding: utf-8 -*-

"""
Band extractor

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

from gdal_image_ulti import save_band_image, copy_spatialref


# --src-file ""
# --target-file ""
# --georef-file ""


def parse_args():
    parser = argparse.ArgumentParser(description='Band extracting for HDF5 Probav data')
    parser.add_argument('--src-file', required=False, type=str, default="./",
                        help='source HDF5 file for band extracting')
    parser.add_argument('--target-file', required=False, type=str, default="./data",
                        help='target file for writing results')
    parser.add_argument('--georef-file', required=False, type=str, default="./data/data.tif",
                        help='spatial reference for results')
    opts = parser.parse_args()
    return opts


class probav_s10_toc_reader(object):
    """

    """

    def __init__(self, src_file):
        self.src_file = src_file
        self.datasource = self._read_probav_s5_toc()

    def get_spatialref(self):
        if self.datasource is None:
            return None

    def get_ndvi_array(self):
        # replace <subdataset> with the number of the subdataset you need, starting with 0
        ndvi_ds = gdal.Open(self.datasource.GetSubDatasets()[6][0], gdal.GA_ReadOnly)
        ndvi_array = ndvi_ds.ReadAsArray()
        print("Shape: {}".format(ndvi_array.shape))
        return ndvi_array

    def get_mask_array(self):
        # replace <subdataset> with the number of the subdataset you need, starting with 0
        mask_ds = gdal.Open(self.datasource.GetSubDatasets()[7][0], gdal.GA_ReadOnly)
        mask_array = mask_ds.ReadAsArray()
        return (mask_array == 248) | (mask_array == 232)

    def _read_probav_s5_toc(self):

        if not gdal.GetDriverByName('HDF5'):
            raise Exception('HDF5 driver is not available')

        hdf5_datasource = gdal.Open(self.src_file, gdal.GA_ReadOnly)
        if hdf5_datasource is not None:
            subdataset = hdf5_datasource.GetSubDatasets()
            # print("Subdataset: ", subdataset)

        return hdf5_datasource

    def _get_product(self, product):
        pass


def ndvi_masked_extract(src_file, target_file, ref_file):
    """

    :param src_file:
    :param target_file:
    :param ref_file:
    :return:
    """
    if os.path.exists(target_file):
        os.remove(target_file)

    dataset = probav_s10_toc_reader(src_file)
    ndvi_array = dataset.get_ndvi_array()
    mask_array = dataset.get_mask_array()
    ndvi_mask = ndvi_array * mask_array

    save_band_image(ndvi_mask, target_file)
    copy_spatialref(ref_file, target_file)


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### Band extractor ########################################")
    print("### ", now)
    print("###########################################################")

    # parameters
    opts = parse_args()
    src_file = opts.src_file
    target_file = opts.target_file
    georef_file = opts.georef_file

    # # test
    # src_file = "F:/application_dataset/africa_grass/s10_r1km_toc/6/PROBAV_S10_TOC_X21Y04/PROBAV_S10_TOC_X21Y04_2020/PROBAV_S10_TOC_X21Y04_20200101_1KM_V101.HDF5"
    # target_file = "F:/application_dataset/africa_grass/s10_r1km_toc/6/PROBAV_S10_TOC_X21Y04/PROBAV_S10_TOC_X21Y04_2020_NDVI/PROBAV_S10_TOC_X21Y04_20200101_1KM_V101.tif"
    # georef_file = "F:/application_dataset/africa_grass/s10_r1km_toc/6/PROBAV_S10_TOC_X21Y04/PROBAV_S10_TOC_X21Y04_1KM.HDF5.tif"

    # run
    ndvi_masked_extract(src_file, target_file, georef_file)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
