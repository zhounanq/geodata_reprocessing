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


def field_calculate(src_path, result_path, mvc_opt='mean', skip_col=6):

    src_df = pd.read_csv(src_path, sep=',', header=0)
    src_header = np.array(src_df.iloc[:, :skip_col])
    src_array = np.array(src_df.iloc[:, skip_col:])

    src_array = src_array.reshape(src_array.shape[0], 10, -1).transpose(0,2,1)
    (row, col, chl) = src_array.shape

    blue_array = src_array[:, :, 0]
    red_array = src_array[:, :, 2]
    nir_array = src_array[:, :, 3]
    ndvi_array = (nir_array - red_array) / (nir_array + red_array)
    evi_array = 2.5*(nir_array - red_array)/(nir_array + 6.0*red_array - 7.5*blue_array + 10000.0)

    b5_array = src_array[:, :, 4]
    b6_array = src_array[:, :, 5]
    b7_array = src_array[:, :, 6]
    s2rep_array = (0.5*(b7_array + nir_array) - b5_array)/(b6_array-b5_array)
    mici_array = (b6_array-b5_array)/(b5_array-nir_array)
    ndrei_array = (b6_array-b5_array)/(b6_array+b5_array)
    ireci_array = (b7_array-nir_array)/(b5_array/b6_array)
    ci_array = b7_array/b5_array
    mcari_array = (b6_array-b5_array-(b6_array-red_array)*0.2)*(b6_array/b5_array)

    concat_pd = [pd.DataFrame(src_header), pd.DataFrame(ndvi_array), pd.DataFrame(evi_array),
                 pd.DataFrame(s2rep_array),pd.DataFrame(mici_array),pd.DataFrame(ndrei_array),
                 pd.DataFrame(ireci_array),pd.DataFrame(ci_array),pd.DataFrame(mcari_array)]
    result_pd = pd.concat(concat_pd, axis=1, ignore_index=False)
    result_pd.to_csv(result_path, float_format='%.4f', header=False, index=False)


def main():
    print("###########################################################")
    print("### ***            ########################################")
    print("###########################################################")

    src_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\dijon_8m\src\parcel_dirong_utm_src_sample5.csv'
    result_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\dijon_8m\src\parcel_dirong_utm_src_sample5_ndvi.csv'

    field_calculate(src_path, result_path)


    print("### Task over #############################################")


if __name__ == "__main__":
    main()