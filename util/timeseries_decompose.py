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
    # IMFs = EMD().emd(tsdata)
    IMFs = EEMD().eemd(tsdata)

    # Plot results
    t = np.linspace(0, 1, len(tsdata))
    N = IMFs.shape[0] + 1

    plt.subplot(N, 1, 1)
    plt.plot(t, tsdata, 'r')
    plt.xlabel("Time [s]")

    for n, imf in enumerate(IMFs):
        plt.subplot(N, 1, n + 2)
        plt.plot(t, imf, 'g')
        plt.title("IMF " + str(n + 1))
        plt.xlabel("Time [s]")

    plt.tight_layout()
    plt.savefig('simple_example')
    plt.show()

    pass


def main():
    print("### Time Series Similiarity ###########################################")

    tscsv_path = 'I:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/csv/flow_2012_2021/flow_2012_2021.csv'
    matrix_path = 'I:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/csv/flow_2012_2021/corr_adj_mat.csv'

    csv_data = read_tsdata(tscsv_path).to_numpy()

    num_col = csv_data.shape[1]
    for idx in range(0, num_col):
        tsdata = csv_data[:,idx]
        timeseries_decompose_emd(tsdata)
    # for

    print('### Task over!')


if __name__ == "__main__":
    main()
