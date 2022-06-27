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


def csv_flipud(srcfile, targetfile):

    src_data = np.loadtxt(srcfile, delimiter=',')

    target_data = np.flipud(src_data)

    np.savetxt(targetfile, target_data, fmt='%.4f', delimiter=',')


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### ***            ########################################")
    print("### ", now)
    print("###########################################################")

    # srcfile = 'J:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/precipitation/0000/prep_run.csv'
    # targetfile = 'J:/FF/application_dataset/AmericanWatershed/01_shape_congaree_river/precipitation/0000/prep_run_r.csv'
    # csv_flipud(srcfile, targetfile)


    print("### Task over #############################################")


if __name__ == "__main__":
    main()
