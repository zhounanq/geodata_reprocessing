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


def csv_select_col(src_path, result_path, col_list, skip_col=6):

    def contain_substr(col_name):
        for sub in col_list:
            if sub in col_name:
                return True
        return False

    src_df = pd.read_csv(src_path, sep=',', header=0)
    col_name_list = src_df.columns[skip_col:].tolist()

    selected_col_name_list = [na for na in col_name_list if not contain_substr(na)]
    res_df = src_df.drop(columns=selected_col_name_list, axis=1)

    res_df.to_csv(result_path, float_format='%.2f', index=False)


def main():
    print("###########################################################")
    print("### ***            ########################################")
    print("###########################################################")

    src_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\dijon_clear\src\parcel_dirong_utm_src.csv'
    result_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\dijon_clear\src\parcel_dirong_utm_src_clear.csv'
    name_list = ['0217', '0227', '0329', '0523', '0617', '0627', '0821', '0826', '0915', '0920']

    csv_select_col(src_path, result_path, col_list=name_list)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
