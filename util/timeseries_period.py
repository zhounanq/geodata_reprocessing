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
import scipy.io as sio
import matplotlib.pyplot as plt
from scipy.fftpack import fft,ifft
from scipy.signal import savgol_filter
from statsmodels import api as sm


def period_fft(ts_array):
    # ts_array = savgol_filter(ts_array, window_length=7, polyorder=3)

    length = len(ts_array)
    yy = fft(ts_array)
    yy_abs = abs(yy)
    yy_abs_normalized = yy_abs/(length/2)
    yy_abs_normalized_half = yy_abs_normalized[range(int(length / 2))]

    # Show
    # plt.figure(figsize=(24, 6))
    #
    # plt.subplot(221)
    # plt.plot(np.arange(length), ts_array)
    # plt.title("Original wave")
    #
    # plt.subplot(222)
    # plt.plot(np.arange(len(yy)), yy_abs, 'r')
    # plt.title("FFT or mixed wave (two sides)")
    #
    # plt.subplot(223)
    # plt.plot(np.arange(len(yy)), yy_abs_normalized, 'g')
    # plt.title("FFT or mixed wave (normalized)")
    #
    # plt.subplot(224)
    # plt.plot(np.arange(len(yy_abs_normalized_half)), yy_abs_normalized_half, 'b')
    # plt.title("FFT or mixed wave")
    # plt.show()

    return yy


def period_acf(ts_array):
    acf = sm.tsa.acf(ts_array, adjusted=True, nlags=len(ts_array), fft=True)

    # plt.figure(figsize = (10, 8))
    # plt.plot(range(0, len(ts_array)), acf)
    # plt.xlim((0, 400))
    # plt.xlabel('Lags (days)')
    # plt.ylabel('Autocorrelation')
    # plt.show()

    return acf


def section_stastis(ts_array2d, sections):

    row, col = ts_array2d.shape
    num_sect = len(sections)+1
    assert((max(sections)<row) and (min(sections)>0))

    section_results = np.zeros((num_sect, col))
    sect_from = 0
    for idx, sect in enumerate(sections):
        sect_data = ts_array2d[sect_from:sect]
        section_results[idx] = np.sum(sect_data, axis=0)
        sect_from = sect
    # for
    section_results[-1] = np.sum(ts_array2d[sect_from:], axis=0)

    return section_results


def main():
    print("### Time Series Similiarity ###########################################")

    tscsv_path = './streamflow-emd/29_imfs.csv'
    csvdata = pd.read_csv(tscsv_path, header=None).to_numpy()

    # num_row = csvdata.shape[0]
    # for idx in range(0, num_row):
    #     tsdata = csvdata[idx]
    #     acf_array = period_acf(tsdata)
    # # for

    # num_row = csvdata.shape[0]
    # for idx in range(0, num_row):
    #     tsdata = csvdata[idx]
    #     fft_array = period_fft(tsdata)
    # # for

    stastis_results = section_stastis(csvdata, sections=[3, 5])

    np.savetxt("./streamflow-emd/29_imfs_compose.csv", stastis_results, fmt='%.4f', delimiter=',')


    print('### Task over!')


if __name__ == "__main__":
    main()
