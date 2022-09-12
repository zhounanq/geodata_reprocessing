# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import datetime
import numpy as np
import pandas as pd


def array_property(numpy_array):

    arr_shape = numpy_array.shape
    arr_size = numpy_array.size
    arr_dtype = numpy_array.dtype

    all_nan = np.isnan(numpy_array).sum()
    row_nan = np.array([np.isnan(row).sum() for row in numpy_array])
    col_nan = np.array([np.isnan(col).sum() for col in numpy_array.T])

    all_nan_ratio = all_nan / arr_size
    row_nan_ratio = row_nan / arr_shape[1]
    col_nan_ratio = col_nan / arr_shape[0]

    np.set_printoptions(formatter={'float_kind': "{:.4f}".format})
    print('array nan ratio is {:.4f}'.format(all_nan_ratio))
    # print('row nan ratio is {}'.format(row_nan_ratio))
    print('col nan ratio is {}'.format(col_nan_ratio))


def mvc_column(src_path, result_path, mvc_opt='mean', mvc_col=4, skip_col=6):

    mvc_function = np.nanmax if mvc_opt=='max' else np.nanmean

    src_df = pd.read_csv(src_path, sep=',', header=0)
    src_header = np.array(src_df.iloc[:, :skip_col])
    src_array = np.array(src_df.iloc[:, skip_col:])
    # array_property(src_array)

    (row, col) = src_array.shape
    assert(col % mvc_col == 0)

    new_col = int(col/mvc_col)
    new_array = np.zeros((row, new_col), dtype=src_array.dtype)
    for cc in range(0, new_col):
        col_array = src_array[:, cc*mvc_col : cc*mvc_col+mvc_col]
        new_col_array = mvc_function(col_array, axis=1)
        new_array[:, cc] = new_col_array[:]
    # for
    array_property(new_array)

    result_pd = pd.concat([pd.DataFrame(src_header), pd.DataFrame(new_array)], axis=1, ignore_index=False)
    result_pd.to_csv(result_path, float_format='%.2f', header=False, index=False)


def main():
    print("###########################################################")
    print("### ***            ########################################")
    print("###########################################################")

    src_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\dijon_8m\src\parcel_dirong_utm_src_sample5.csv'
    result_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\dijon_8m_12mean\src\parcel_dirong_utm_src_sample5.csv'

    mvc_column(src_path, result_path, mvc_opt='mean', mvc_col=12)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
