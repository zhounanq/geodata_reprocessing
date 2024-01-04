# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray


def l2b_shapefile(l2b_path, shape_path):

    l2b_ds = xarray.open_dataset(l2b_path, group='PRODUCT')

    data = l2b_ds['SIF_743'].values
    lon = l2b_ds['longitude'].values
    lat = l2b_ds['latitude'].values

    dat = pd.DataFrame({'lon': lon, 'lat': lat, 'sif743': data})
    geom = gpd.points_from_xy(dat['lon'], dat['lat'], crs=4326)
    geo_dat = gpd.GeoDataFrame(data=dat[['sif743']], geometry=geom)
    # geo_dat.plot(column='sif743', legend=True, markersize=1)

    geo_dat.to_file(shape_path, driver='ESRI Shapefile', encoding='utf-8')
    l2b_ds.close()
    return shape_path


l2b_path = r'D:\TROPOSIF_L2B_2018-05-01.nc'
shape_path = r'D:\TROPOSIF_L2B_2018-05-01.nc.shp'


l2b_shapefile(l2b_path, shape_path)
