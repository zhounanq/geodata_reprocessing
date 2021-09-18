# -*- coding: utf-8 -*-

"""
Maximum(Mean) value composite of NDVI

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

# --src-folder "H:\FF\application_dataset\africa_grass\PROBAV_S5\PROBAV_S5_TOC_X17Y04_2019060"
# --target-file "H:\FF\application_dataset\africa_grass\PROBAV_S5\PROBAV_C55_TOC_X17Y04_20190601_100M.tif"
# --georef-file "H:/FF/application_dataset/africa_grass/PROBAV_S5_TOC_X17Y04/spatialref/PROBAV_S5_TOC_X17Y04_100M_V101.HDF5.tif"


def parse_args():
    parser = argparse.ArgumentParser(description='NDVI max(mean) composite for Probav data')
    parser.add_argument('--src-folder', required=False, type=str, default="./",
                        help='source folder containing files for composition')
    parser.add_argument('--target-file', required=False, type=str, default="./data",
                        help='target file for writing results')
    parser.add_argument('--georef-file', required=False, type=str, default="./data/data.tif",
                        help='spatial reference for results')
    parser.add_argument('--operator', required=False, type=str, default="max", help='stistic operator')
    opts = parser.parse_args()
    return opts


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
    img_shape = img_array.shape

    file_format = format
    file_driver = gdal.GetDriverByName(file_format)
    metadata = file_driver.GetMetadata()
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports Create() method.".format(file_format))
    if metadata.get(gdal.DCAP_CREATE) == "YES":
        print("Driver {} supports CreateCopy() method.".format(file_format))

    dst_ds = file_driver.Create(save_path, xsize=img_shape[1], ysize=img_shape[0], bands=1, eType=gdal.GDT_Float32)
    if not dst_ds:
        print("Fail to create image {}".format(save_path))
        return False
    dst_ds.GetRasterBand(1).WriteArray(img_array)

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


class probav_s5_toc_reader(object):
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
        return (mask_array==248)

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


def ndvi_composites(src_files, target_file, ref_file, operator="max"):

    if os.path.exists(target_file):
        os.remove(target_file)

    ndvi_mask = []
    for i, file in enumerate(src_files):
        dataset = probav_s5_toc_reader(file)
        ndvi_array = dataset.get_ndvi_array()
        mask_array = dataset.get_mask_array()
        ndvi_mask.append(ndvi_array * mask_array)

    max_composite = np.maximum.reduce([r for r in ndvi_mask])

    save_band_image(max_composite, target_file)
    copy_spatialref(ref_file, target_file)


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### NDVI max(mean) composite ##############################")
    print("### ", now)
    print("###########################################################")

    opts = parse_args()
    folder = opts.src_folder
    target_file = opts.target_file
    georef_file = opts.georef_file
    operator = opts.operator

    src_files = []
    folder_list = os.listdir(folder)
    for df in folder_list:
        src_df = os.path.join(folder, df)
        if os.path.isfile(src_df):
            src_files.append(src_df)
    #for

    ndvi_composites(src_files, target_file, georef_file, operator)

    # # test gdal reader
    # probav_s5_toc_file = "H:/FF/application_dataset/africa_grass/PROBAV_S5_TOC_X17Y04/PROBAV_S5_TOC_X17Y04_20200101_100M_V101.HDF5"
    # hdf_reader = probav_s5_toc_reader(probav_s5_toc_file)

    # # test mvc
    # probav_s5_toc_1 = "H:/FF/application_dataset/africa_grass/PROBAV_S5_TOC_X17Y04/PROBAV_S5_TOC_X17Y04_20200101_100M_V101.HDF5"
    # probav_s5_toc_2 = "H:/FF/application_dataset/africa_grass/PROBAV_S5_TOC_X17Y04/PROBAV_S5_TOC_X17Y04_20200106_100M_V101.HDF5"
    # target_file = "H:/FF/application_dataset/africa_grass/PROBAV_S5_TOC_X17Y04/mvc/PROBAV_C55_TOC_X17Y04_20200101_100M.tif"
    # georef_file = "H:/FF/application_dataset/africa_grass/PROBAV_S5_TOC_X17Y04/spatialref/PROBAV_S5_TOC_X17Y04_100M_V101.HDF5.tif"
    #
    # src_files = [probav_s5_toc_1, probav_s5_toc_2]
    # ndvi_composites(src_files, target_file, georef_file)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
