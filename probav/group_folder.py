# -*- coding: utf-8 -*-

"""
Maximum(Mean) value composite of NDVI

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import time
import datetime
import shutil
import argparse


def group_folder_s5_s10(folder):
    prefix = "PROBAV_S5_TOC_X17Y04_2019060"

    if not os.path.exists(folder):
        raise Exception("### {} not exist".format(folder))

    folder_list = os.listdir(folder)
    for df in folder_list:
        src_df = os.path.join(folder, df)
        if os.path.isfile(src_df):
            basename = os.path.basename(src_df)
            sub_folder = basename[:len(prefix)]
            sub_folder = os.path.join(folder, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
            new_df = os.path.join(sub_folder, basename)
            shutil.move(src_df, new_df)
            print("### {} -> {}".format(src_df, new_df))
    pass


def main():
    folder = "H:/FF/application_dataset/africa_grass/PROBAV_S5/"

    group_folder_s5_s10(folder)

    pass


if __name__ == "__main__":
    main()