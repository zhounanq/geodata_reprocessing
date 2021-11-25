# -*- coding: utf-8 -*-

"""
Time series plotting

Author: Zhou Ya'nan
Date: 2021-10-16
"""
import os
import datetime
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.signal import savgol_filter


def sg_filter(src_timeseries):
    filtered_timeseries = savgol_filter(src_timeseries, window_length=7, polyorder=3)
    return filtered_timeseries


def yige_detection_1(tsdata):
    """
    PROBAV_S10_TOC_X17Y04
    PROBAV_S10_TOC_X21Y04
    """
    column = tsdata.columns.values
    column = [col[1:] for col in column]

    results_arr = []

    for index, row in tsdata.iterrows():
        src_data = row
        yige_locations = []
        sgfiltered_data = sg_filter(src_data)

        # is grass land or not?
        row_max = np.max(src_data)

        if row_max>60:

            # 计算波峰波谷, 二次差分
            doublediff = np.diff(np.sign(np.diff(src_data)))
            peak_locations = np.where(doublediff == -2)[0] + 1
            doublediff = np.diff(np.sign(np.diff(-1 * src_data)))
            trough_locations = np.where(doublediff == -2)[0] + 1

            diff_data = np.diff(src_data)
            for peak in peak_locations:
                if (src_data[peak]<60) or (peak>27) or (peak<3):
                    continue
                if (peak+1) in trough_locations:
                    if (diff_data[peak-1]<5) and (diff_data[peak]<-15) and (diff_data[peak+1]>5):
                        yige_locations = np.append(yige_locations, peak)
                        continue
                if (diff_data[peak]<-35) and (peak>12) and (peak<25):
                    yige_locations = np.append(yige_locations, peak)
                    continue
            # for
        # if

        # store string
        yege_str = ','.join(str(i) for i in yige_locations)
        results_arr = np.append(results_arr, yege_str)

        # flot
        if len(yige_locations) > 0:
            print("### YIGE @ {}".format(yige_locations))
        # fig = plt.figure(figsize=(12, 4))
        # plt.plot(column, src_data, color='tab:blue', label="src", linestyle='-', linewidth=1)
        # plt.plot(column, sgfiltered_data, color='deeppink', label="s-g", linestyle='-', linewidth=1)
        # if len(yige_locations) > 0:
        #     locations = np.array(yige_locations, dtype=int)
        #     plt.scatter(np.array(column)[locations], np.array(src_data)[locations],
        #                 marker=mpl.markers.CARETUPBASE, color='tab:green', s=32, label='YG')
        # plt.legend()
        # plt.show()
    # for
    # insert one column
    tsdata["yige"] = results_arr

    # return
    return tsdata


def yige_detection(tsdata):
    column = tsdata.columns.values
    column = [col[1:] for col in column]

    results_arr = []

    for index, row in tsdata.iterrows():
        src_data = row
        yige_locations = []
        sgfiltered_data = sg_filter(src_data)

        # is grass land or not?
        row_max = np.max(src_data)

        # number of elements with value == 0
        zero_num = np.sum(src_data<10)

        if (row_max>80) and (zero_num<2):

            # 计算波峰波谷, 二次差分
            doublediff = np.diff(np.sign(np.diff(src_data)))
            peak_locations = np.where(doublediff == -2)[0] + 1
            doublediff = np.diff(np.sign(np.diff(-1 * src_data)))
            trough_locations = np.where(doublediff == -2)[0] + 1

            diff_data = np.diff(src_data)
            for peak in peak_locations:
                if (src_data[peak]<60) or (peak>27) or (peak<3):
                    continue
                if (peak+1) in trough_locations:
                    if (diff_data[peak-1]<5) and (diff_data[peak]<-15) and (diff_data[peak+1]>5):
                        yige_locations = np.append(yige_locations, peak)
                        continue
                if (diff_data[peak]<-35) and (peak>12) and (peak<25):
                    yige_locations = np.append(yige_locations, peak)
                    continue
            # for
        # if

        # store string
        yege_str = ','.join(str(i) for i in yige_locations)
        results_arr = np.append(results_arr, yege_str)

        # flot
        if len(yige_locations) > 0:
            print("### YIGE @ {} @ {}".format(index, yige_locations))
        # fig = plt.figure(figsize=(12, 4))
        # plt.plot(column, src_data, color='tab:blue', label="src", linestyle='-', linewidth=1)
        # plt.plot(column, sgfiltered_data, color='deeppink', label="s-g", linestyle='-', linewidth=1)
        # if len(yige_locations) > 0:
        #     locations = np.array(yige_locations, dtype=int)
        #     plt.scatter(np.array(column)[locations], np.array(src_data)[locations],
        #                 marker=mpl.markers.CARETUPBASE, color='tab:green', s=32, label='YG')
        # plt.legend()
        # plt.show()
    # for
    # insert one column
    tsdata["yige"] = results_arr

    # return
    return tsdata


def read_tsdata(data_file):
    data_pd = pd.read_csv(data_file, header=0)
    tsprefix_pd = data_pd.iloc[:, :7]
    tsdata_pd = data_pd.iloc[:, 7:]

    return tsprefix_pd, tsdata_pd


def plot_timeseries(ts_x, ts_data, filtered_data=None):

    fig = plt.figure(figsize=(12,4))
    plt.plot(ts_x, ts_data, color='tab:blue', label="src", linestyle='-',linewidth=1)
    if filtered_data is not None:
        plt.plot(ts_x, filtered_data, color='deeppink', label="s-g", linestyle='-',linewidth=1)

    plt.legend()
    plt.show()


def plot_tsdata(tsdata):

    column = tsdata.columns.values
    column = [col[1:] for col in column]

    # for index, row in tsdata.iterrows():
    #     src_data = row
    #     sgfiltered_data = sg_filter(src_data)
    #     plot_timeseries(column, src_data, sgfiltered_data)

    for index in range(0, len(tsdata), 5000):
        src_data = tsdata.iloc[index]
        sgfiltered_data = sg_filter(src_data)
        plot_timeseries(column, src_data, sgfiltered_data)

    pass


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### Band extractor ########################################")
    print("### ", now)
    print("###########################################################")

    csvdata_file = "I:/FF/application-project/2021-africagrass/PROBAV/6/PROBAV_S10_TOC_X21Y06/shp/csv/pixel_tsattri_2020.csv"
    target_file = "I:/FF/application-project/2021-africagrass/PROBAV/6/PROBAV_S10_TOC_X21Y06/shp/csv/pixel_tsattri_2020_yige.csv"

    tsprefix_pd, tsdata_pd = read_tsdata(csvdata_file)

    # plot_tsdata(tsdata_pd)
    yige_pd = yige_detection(tsdata_pd)

    yige_pd.to_csv(target_file)



    print("### Task over #############################################")


if __name__ == "__main__":
    main()
