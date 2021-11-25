# -*- coding: utf-8 -*-

"""
Image operations

Author: Zhou Ya'nan
"""
import os
import datetime
import argparse
import math
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Seasonal Decomposition by Moving Averages
from statsmodels.tsa.seasonal import seasonal_decompose
# Season-Trend decomposition using LOESS.
from statsmodels.tsa.seasonal import STL
from PyEMD import EMD, EEMD, CEEMDAN
import pylab as plt


def read_tsdata(csvdata_path):
    csvdata_pd = pd.read_csv(csvdata_path, header=None)

    csvdata_pd = csvdata_pd.fillna(method='pad', axis=0)

    return csvdata_pd


def timeseries_decompose_stl(tsdata, period):

    result_add = STL(tsdata, period=period).fit()

    # plt.rcParams.update({'figure.figsize': (10, 10)})
    # result_add.plot()
    # plt.show()

    return result_add


def timeseries_decompose_emd(tsdata):
    IMFs = EMD().emd(tsdata)
    # IMFs = EEMD().eemd(tsdata)

    # # Plot results
    # t = np.linspace(0, 1, len(tsdata))
    # N = IMFs.shape[0] + 1
    #
    # plt.subplot(N, 1, 1)
    # plt.plot(t, tsdata, 'r')
    # plt.xlabel("Time [s]")
    #
    # for n, imf in enumerate(IMFs):
    #     plt.subplot(N, 1, n + 2)
    #     plt.plot(t, imf, 'g')
    #     plt.title("IMF " + str(n + 1))
    #     plt.xlabel("Time [s]")
    #
    # plt.tight_layout()
    # plt.savefig('simple_example')
    # plt.show()

    return IMFs


def merge_decomposition(src_folder, tag_folder):

    file_list = []

    item_list = os.listdir(src_folder)
    for item_path in item_list:
        abs_path = os.path.join(src_folder, item_path)
        if os.path.isfile(abs_path):
            print(abs_path)
            file_list.append(abs_path)
        # if
    # for
    num_data = len(file_list)

    # read first file for meta info
    csvdata = pd.read_csv(file_list[0], header=None).to_numpy()
    row, col = csvdata.shape

    all_data = np.zeros((num_data, row, col))
    for idx, path in enumerate(file_list):
        csvdata = pd.read_csv(path, header=None).to_numpy()
        all_data[idx] = csvdata
    # for

    all_data = all_data.transpose(1, 0, 2)
    for idx in range(row):
        tag_path = os.path.join(tag_folder, "compose_{}.csv".format(idx))
        np.savetxt(tag_path, all_data[idx].T, fmt='%.4f', delimiter=',')
    # for

    pass


def main():
    print("### Time Series Similiarity ###########################################")

    # tscsv_path = 'D:/flow_2012_2021.csv'
    # csv_data = read_tsdata(tscsv_path).to_numpy()
    #
    # num_col = csv_data.shape[1]
    # for idx in range(0, num_col):
    #     tsdata = csv_data[:,idx]
    #     imfs = timeseries_decompose_emd(tsdata)
    #     np.savetxt("./streamflow-emd/{}_imfs.csv".format(idx), imfs, fmt='%.4f', delimiter=',')
    # # for


    src_folder = './streamflow-emd/compose_adjust/'
    tag_folder = './streamflow-emd/'

    merge_decomposition(src_folder, tag_folder)

    print('### Task over!')


if __name__ == "__main__":
    main()
