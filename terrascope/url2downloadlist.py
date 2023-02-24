# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import json
import requests


def url2list(url, ):
    try:
        url_result = requests.get(url)
    except Exception as e:
        print('### Error: %s' % e)
        return None

    # url_json = url_result.json()
    if url_result.status_code == 200:
        return url_result.content
    else:
        print('### Error: {}'.format(url_result.status_code))
        return None


def html2json(html, ):

    html_json = json.loads(html)

    features = html_json['features']
    for feat in features:
        links = feat['properties']['links']
        related = links['related'][0]['href']
        data = links['data'][0]['href']
        # previews = links['previews'][1]['href']
        alternates = links['alternates'][0]['href']
        print(related)
        print(data)
        # print(previews)
        print(alternates)

    return html_json


def main():
    print("###########################################################")
    print("### ***            ########################################")
    print("###########################################################")

    # cmd line
    # opts = parse_args()
    # hdf_path = opts.src_hdf
    # save_path = opts.target_raster
    # spatial_ref_path = ''

    # for test
    url = 'https://services.terrascope.be/catalogue/products?collection=urn:eop:VITO:TERRASCOPE_S2_FCOVER_V2&start=2021-03-01T00:00:00.000Z&end=2021-12-31T23:59:59.000Z&geometry=POLYGON((-5.290703617889902%2040.9519125658866,-5.299646384385757%2040.719614270628,-5.1416575096256265%2040.85277793617206,-5.290703617889902%2040.9519125658866))&sortKeys=title,,0,0&resolution=%7B20%7D&tileId=30TUL'
    html_content = ''

    html_content = url2list(url)
    html_json = html2json(html_content)

    print("### Task over #############################################")


if __name__ == "__main__":
    main()
