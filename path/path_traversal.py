# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import datetime


def traversal_dir(dir_path):
    if not os.path.exists(dir_path):
        print("### Wrong: {} not exist".format(dir_path))

    item_list = os.listdir(dir_path)
    for item_path in item_list:
        abs_path = os.path.join(dir_path, item_path)
        if os.path.isfile(abs_path):
            print(abs_path)
        # if
    # for
    pass


def main():
    now = datetime.datetime.now()
    print("###########################################################")
    print("### ***            ########################################")
    print("### ", now)
    print("###########################################################")



    print("### Task over #############################################")


if __name__ == "__main__":
    main()
