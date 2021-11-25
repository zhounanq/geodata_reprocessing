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


def csv_merge_folder(src_folder, target_file):

    if not os.path.exists(src_folder):
        print("### Wrong: {} not exist".format(src_folder))
    item_list = os.listdir(src_folder)

    csvfile_list = []
    for item_path in item_list:
        abs_path = os.path.join(src_folder, item_path)
        if os.path.isfile(abs_path) and (item_path.find('.csv')>=0):
            print(abs_path)
            csvfile_list.append(abs_path)
        # if
    # for

    csvdata = []
    for csvfile in csvfile_list:
        csv_pd = pd.read_csv(csvfile, header=0)
        target_col = csv_pd.iloc[:, -1].to_numpy().T
        csvdata.append(target_col)
    # for

    np.savetxt(target_file, csvdata, fmt='%.4f', delimiter=',')
    pass


def csv_merge_folder2(src_folder, target_file):

    if not os.path.exists(src_folder):
        print("### Wrong: {} not exist".format(src_folder))
    item_list = os.listdir(src_folder)

    csvfile_list = []
    for item_path in item_list:
        abs_path = os.path.join(src_folder, item_path)
        if os.path.isfile(abs_path) and (item_path.find('.csv') >= 0):
            print(abs_path)
            csvfile_list.append(abs_path)
        # if
    # for

    target_pd = pd.DataFrame()
    for csvfile in csvfile_list:
        csv_pd = pd.read_csv(csvfile, header=None)
        target_pd = target_pd.append(csv_pd)
    # for
    target_pd_r = target_pd.iloc[::-1]

    np.savetxt(target_file, target_pd_r.to_numpy(), fmt='%.4f', delimiter=',')
    pass


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### ***            ########################################")
    print("### ", now)
    print("###########################################################")

    # src_folder = 'G:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/precipitation/2012/'
    # target_file = 'G:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/precipitation/2012/2012.csv'
    # csv_merge_folder(src_folder, target_file)

    src_folder = 'G:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/precipitation/0000/'
    target_file = 'G:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/precipitation/0000/0000.csv'
    csv_merge_folder2(src_folder, target_file)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
