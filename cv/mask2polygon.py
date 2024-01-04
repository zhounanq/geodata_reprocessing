# -*- utf-8 -*-
# @Time: 2022/9/27 22:02
# @Author:
# @File:
# @Software: PyCharm
import os
import numpy as np
import geojson
import fiona
import json
import geopandas as gpd
import rasterio
from rasterio import features
from shapely.geometry import Polygon


def labelme_json_to_shape_file(src_json_file, dst_shape_file, ref_raster_file):
    """
    将labelme标注的json文件转换为shape文件.
    """

    # Load the polygon JSON file
    with open(src_json_file) as f:
        json_data = json.load(f)

    # Load the raster file
    with rasterio.open(ref_raster_file) as src:
        src_crs = src.crs
        transform = src.transform

    # Extract coordinates and labels from the JSON data
    labels, geometries = [], []
    for shape in json_data['shapes']:
        geometry_type = shape['shape_type']

        if geometry_type == 'rectangle':
            label = shape['label']
            points_raw = shape['points']

            # Transform all input coordinates to geographic coordinates (longitude, latitude)
            points_raw = [list(transform * (point[0], point[1])) for point in points_raw]
            points_converted = [
                [points_raw[0][0], points_raw[0][1]],
                [points_raw[0][0], points_raw[1][1]],
                [points_raw[1][0], points_raw[1][1]],
                [points_raw[1][0], points_raw[0][1]],
                [points_raw[0][0], points_raw[0][1]]
            ]

            geometries.append(points_converted)
            labels.append(label)

        elif geometry_type == 'polygon':
            label = shape['label']
            points_raw = shape['points']

            # Transform all input coordinates to geographic coordinates (longitude, latitude)
            points_converted = [list(transform * (point[0], point[1])) for point in points_raw]

            geometries.append(points_converted)
            labels.append(label)

    # Create GeoDataFrame using extracted geometries and labels
    gdf = gpd.GeoDataFrame({'geometry': geometries, 'label': labels})
    gdf.geometry = gdf.apply(lambda row: Polygon(row.geometry), axis=1)
    # Set CRS of GeoDataFrame same as that of the raster dataset
    gdf.crs = src_crs

    # Save GeoDataFrame as Shapefile with correct projection information from raster dataset
    gdf.to_file(dst_shape_file, driver='ESRI Shapefile', spatial_reference=src_crs)

    return dst_shape_file


def shape_file_to_labelme_json(src_shape_file, dst_json_file, ref_raster_file):
    """
    将shape文件转换为labelme标注的json文件，统一为labelme的polygon标注.
    """

    # Create a dictionary for the Labelme JSON structure
    labelme_dict = {
        "version": "4.5.6",
        "flags": {},
        "shapes": []
    }

    # Load the raster file
    with rasterio.open(ref_raster_file) as src:
        transform = src.transform

    # Read the shapefile using geopandas
    gdf = gpd.read_file(src_shape_file)

    # Iterate over each feature in the GeoDataFrame
    for idx, row in gdf.iterrows():
        # Extract geometry coordinates from each feature
        coords = row.geometry.exterior.coords[:-1]  # Exclude last point (it repeats first point)

        # Transform all input coordinates to geographic coordinates (longitude, latitude)
        coords = [list(~transform * (point[0], point[1])) for point in coords]

        # Create a dictionary for each label shape in Labelme format
        shape_dict = {
            "label": row['label'],  # Replace with your desired class labels or attribute names from Shapefile
            "points": coords,
            "group_id": None,
            "shape_type": 'polygon',
            "flags": {}
        }

        # Append this shape dictionary to list of shapes in labelme_dict
        labelme_dict["shapes"].append(shape_dict)
    # for

    # Convert dictionary to JSON string representation
    json_str = json.dumps(labelme_dict, indent=2)

    # Save JSON string to output file (*.json)
    with open(dst_json_file, 'w') as f:
        f.write(json_str)

    return dst_json_file


def mask2shp(src_mask_list, dst_shape_file, ref_raster_file):
    """
    以raster为地理参考，将mask列表转换为shape文件.
    """
    # Generate vector shapes from the raster image using polygonize function of gdal library.
    with rasterio.open(ref_raster_file) as src:
        feats = (
            {'properties': {'value': v}, 'geometry': s}
            for mask in src_mask_list
            for i, (s, v) in enumerate(features.shapes(mask.astype(int), transform=src.transform)) if v != 0
        )

    # Create output schema for the Shapefile format with attribute "value" of type integer.
    schema = {
        'geometry': 'Polygon',
        'properties': {'value': 'int'},
    }
    # Write each polygon feature to a new Shapefile
    with fiona.open(dst_shape_file, 'w', driver='ESRI Shapefile', crs=src.crs, schema=schema) as dst:
        for feat in feats:
            dst.write(feat)

    return dst_shape_file


def mask2geojson(mask_list, geojson_path, raster_path):
    """

    """
    # Generate vector shapes from the raster image using polygonize function of gdal library.
    with rasterio.open(raster_path) as src:
        feats = (
            {'properties': {'value': v}, 'geometry': s}
            for mask in mask_list
            for i, (s, v) in enumerate(features.shapes(mask.astype(int), transform=src.transform)) if v != 0
        )

    # 构建GeoJson
    feat_list = list(feats)
    feature_collection = geojson.FeatureCollection(feat_list)

    # Save GeoJSON feature collection to a file
    with open(geojson_path, 'w') as f:
        geojson.dump(feature_collection, f)

    return geojson_path


def main():
    print("############################################################")

    # args = get_arguments()
    # print("Args:", args)

    # src_json_file = r"D:\I48H143156_1_1.bbox.json"
    # dst_shape_file = r"D:\I48H143156_1_1.bbox.json.shp"
    # ref_raster_file = r"D:\I48H143156_1_1.tif"
    # labelme_json_to_shape_file(src_json_file, dst_shape_file, ref_raster_file)

    src_shape_file = r"D:\I48H143156_1_1.bbox.json.shp"
    dst_json_file = r"D:\I48H143156_1_1.bbox.json.shp.json"
    ref_raster_file = r"D:\I48H143156_1_1.tif"
    shape_file_to_labelme_json(src_shape_file, dst_json_file, ref_raster_file)


if __name__ == "__main__":
    main()
