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


def pandas_fill_nan():


    pass



def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### ***            ########################################")
    print("### ", now)
    print("###########################################################")

    src_csv_path = r'F:\application_dataset\CovidVegGreen\h27v05\lst_wuhan\wh_re_mvc_nz1.csv'
    dst_csv_path = r'F:\application_dataset\CovidVegGreen\h27v05\lst_wuhan\wh_re_mvc_nz.csv'

    src_df = pd.read_csv(src_csv_path, header=0)

    # src_df.replace(-9999, np.nan)
    src_df[src_df < 0] = np.nan
    src_df.interpolate(inplace=True, axis=1)

    src_df.to_csv(dst_csv_path, index=False, float_format='%.2f')



    print("### Task over #############################################")


if __name__ == "__main__":
    main()
