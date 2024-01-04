# -*- coding: utf-8 -*-

"""
Functions for image operation in gdal

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import rasterio
import numpy as np


def invalid_pixel_mask_expend(input_raster, output_raster):

    with rasterio.open(input_raster) as src_dataset:
        profile = src_dataset.profile

        # raster_array = src_dataset.read() # read all bands
        band_array = src_dataset.read(1)
        invalid_mask = (band_array == 0)
        height, width = invalid_mask.shape

        invalid_mask_expend = np.zeros(shape=(height+2, width+2), dtype=np.uint8)
        for hh in range(height):
            for ww in range(width):
                if invalid_mask[hh, ww]==True:
                    # invalid_mask_expend[hh  , ww  ] = 1
                    # invalid_mask_expend[hh  , ww+1] = 1
                    # invalid_mask_expend[hh  , ww+2] = 1
                    # invalid_mask_expend[hh+1, ww  ] = 1
                    # invalid_mask_expend[hh+1, ww+1] = 1
                    # invalid_mask_expend[hh+1, ww+2] = 1
                    # invalid_mask_expend[hh+2, ww  ] = 1
                    # invalid_mask_expend[hh+2, ww+1] = 1
                    # invalid_mask_expend[hh+2, ww+2] = 1
                    for h in range(3):
                        for w in range(3):
                            invalid_mask_expend[hh + h, ww + w] = 1
        invalid_mask_expend = invalid_mask_expend[1:-1, 1:-1]

        profile.update(
            dtype=np.uint8,
            count=1
        )
        '''you can also using ...
        with rasterio.open('NDVI.tif', mode='w', driver='GTiff',
                           width=src.width, height=src.height, count=1,
                           crs=src.crs, transform=src.transform, dtype=np.uint8) as dst:
        '''
        with rasterio.open(output_raster, mode='w', **profile) as dst_dataset:
            dst_dataset.write(invalid_mask_expend, 1)
        # with
    # with

    return output_raster


def main():
    print("#############################################################")

    input_raster = r''
    output_raster = r''
    invalid_pixel_mask_expend(input_raster, output_raster)

    print("### Task is over!")


if __name__ == "__main__":
    main()
