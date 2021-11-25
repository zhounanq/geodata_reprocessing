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

from sklearn import preprocessing
import dtw



def read_tsdata(csvdata_path):
    csvdata_pd = pd.read_csv(csvdata_path, header=None)

    csvdata_pd = csvdata_pd.fillna(method='pad', axis=0)

    return csvdata_pd


def data_normalized(csv_data, normalize_method='z_score', norm_statistic=None):
    """
    The data used to compute the mean and standard deviation used for later scaling along the features axis.
    """
    if normalize_method == 'min_max':
        if not norm_statistic:
            norm_statistic = preprocessing.MinMaxScaler().fit(csv_data)
        trans_data = norm_statistic.transform(csv_data)
    elif normalize_method == 'z_score':
        if not norm_statistic:
            norm_statistic = preprocessing.StandardScaler().fit(csv_data)
        trans_data = norm_statistic.transform(csv_data)
    return trans_data, norm_statistic


def calculate_dtw(x, y, dist=None):
    l1_norm = lambda x, y: np.abs(x - y)
    l2_norm = lambda x, y: (x - y) ** 2
    # dist, cost, acc, path = dtw.dtw(x, y, dist=l2_norm)

    # The called fun in accelarated_dtw is prowerful
    # metric : str or callable, optional
    #     The distance metric to use.  If a string, the distance function can be
    #     'braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation',
    #     'cosine', 'dice', 'euclidean', 'hamming', 'jaccard', 'jensenshannon',
    #     'kulsinski', 'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto',
    #     'russellrao', 'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
    #     'wminkowski', 'yule'.
    dist, cost, acc, path = dtw.accelerated_dtw(x, y, dist='euclidean')
    return dist


def dtw_matrix(data_array):
    """
    DTW distance between two columns.
    :param data_array:
    :return:
    """
    num_note = data_array.shape[1]
    similar_matrix = np.zeros([num_note, num_note])
    for c1 in range(0,num_note):
        ts1 = data_array[:, c1].reshape(-1, 1)
        for c2 in range(0,c1):
            ts2 = data_array[:, c2].reshape(-1, 1)
            dist = calculate_dtw(ts1, ts2)
            similar_matrix[c1][c2] = dist
            similar_matrix[c2][c1] = dist
        # for
    # for
    return similar_matrix


def dtw2adj_matrix(dtw_matrix, normalize_method='min_max'):
    """

    :param dtw_matrix: numpy array
    :param normalize_method:
    :return:
    """
    src_shape = dtw_matrix.shape
    trans_data = dtw_matrix.reshape([-1,1])

    if normalize_method == 'min_max':
        trans_data = preprocessing.MinMaxScaler().fit_transform(trans_data)
    elif normalize_method == 'z_score':
        trans_data = preprocessing.MinMaxScaler().fit_transform(trans_data)
    trans_data = 1.0 - trans_data

    trans_data = trans_data.reshape(src_shape)
    return trans_data


def correlation_matrix(data_array, method="pearson"):
    """
    Correlation between two column.
    :param data_array:
    :param method:
    :return:
    """
    correlation_matrix = pd.DataFrame(data_array).corr(method)
    correlation_matrix = correlation_matrix.to_numpy()
    return correlation_matrix


def write_similiarity_matrix(matrix_path, similiar_matrix):
    np.savetxt(matrix_path, similiar_matrix, fmt='%.4f', delimiter=',')


def main():
    print("### Time Series Similiarity ###########################################")

    tscsv_path = 'I:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/csv/flow_2012_2021/flow_2012_2021.csv'
    matrix_path = 'I:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/csv/flow_2012_2021/corr_adj_mat.csv'

    csv_data = read_tsdata(tscsv_path)
    normalized_data, _ = data_normalized(csv_data)

    # correlation matrix
    correlation_matrix = pd.DataFrame(normalized_data).corr()
    adj_matrix = correlation_matrix.to_numpy()

    # # DTW similiarity matrix
    # dtw_distance_matrix = dtw_matrix(normalized_data)
    # adj_matrix = dtw2adj_matrix(dtw_distance_matrix)

    # Show
    similar_matrix = np.around(adj_matrix, 6)
    sns.heatmap(similar_matrix, cmap='Blues', annot=False)
    plt.show()

    # Save
    write_similiarity_matrix(matrix_path, similar_matrix)

    print('### Task over!')


if __name__ == "__main__":
    main()
