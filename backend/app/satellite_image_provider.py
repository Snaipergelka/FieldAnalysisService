import os

import rasterio
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

from utils import unzip_files


class SatelliteDataProvider:
    def __init__(self, api_client):
        self.client = api_client

    def get_data(self, footprint, output_folder="satellite_data"):
        """
        Gets data from api by footprint

        :param footprint:
        :param output_folder:
        :return: path to zipped data
        """

        # search by polygon, time, and SciHub query keywords
        products = self.client.query(footprint,
                                     date=('20220101', '20220605'),
                                     platformname='Sentinel-2',
                                     cloudcoverpercentage=(0, 10))

        # convert to Pandas DataFrame
        products_df = self.client.to_dataframe(products)

        # sort and limit to first best product
        products_df_sorted = products_df.sort_values(
            ['cloudcoverpercentage', 'ingestiondate'],
            ascending=[True, True]
        )
        products_df_sorted = products_df_sorted.iloc[0]
        title = products_df_sorted['title']
        m_uuid = products_df_sorted['uuid']

        # download best results from the search
        self.client.download(id=m_uuid, directory_path=output_folder)

        # return path to downloaded data
        return os.path.join(output_folder, title)


class SciHubSatelliteDataExtractor:
    """
    This class is responsible for parsing data and files structure
    received from SciHub site.
    The problem is that directories and files have dynamic names based on date.
    Example:  'data/S2A_MSIL2A_20220601T080611_N0400_R078_T39VVG_20220601T120411.SAFE/
                GRANULE/L2A_T39VVG_A036254_20220601T081244/IMG_DATA/R10m'
    """

    def __init__(self, path_to_data):
        self.path = path_to_data

    def __extract_base_path(self, resolution):

        res = [p for p in os.walk(self.path)
               if "GRANULE" in p[0]
               and "IMG_DATA" in p[0]
               and resolution in p[0]]

        if len(res) == 0:
            raise Exception("Impossible to parse provided folder. Please check if path is correct!")

        return res[0]

    def extract_nir_image_path(self, resolution='R10m'):
        bp = self.__extract_base_path(resolution)
        nir = [p for p in bp[2] if "B08" in p][0]
        return os.path.join(bp[0], nir)

    def extract_red_image_path(self, resolution="R10m"):
        bp = self.__extract_base_path(resolution)
        red = [p for p in bp[2] if "B04" in p][0]
        return os.path.join(bp[0], red)


def calculate_nvdi(path_to_data):
    """
    TODO Должна быть в итоге независима от загрузки картинок.
        Например, потому что могут быть разные форматы картинок.

    nir - red /(nir + red)
    :return:
    """

    # Open b4 and b8
    b4 = rasterio.open(path_to_data + '/T39VVG_20220601T080611_B04_10m.jp2')
    b8 = rasterio.open(path_to_data + '/T39VVG_20220601T080611_B08_10m.jp2')

    # read Red(b4) and NIR(b8) as arrays
    red = b4.read()
    nir = b8.read()

    # Calculate ndvi
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

    # Write the NDVI image
    meta = b4.meta
    meta.update(driver='GTiff')
    meta.update(dtype=rasterio.float32)

    with rasterio.open('NDVI.tif', 'w', **meta) as dst:
        dst.write(ndvi.astype(rasterio.float32))


if __name__ == "__main__":
    # api = SentinelAPI(
    #     os.environ.get("USER"),
    #     os.environ.get("PASSWORD"),
    #     os.environ.get("API_URL"))
    # dp_client = SatelliteDataProvider(api_client=api)
    #
    # fp = geojson_to_wkt(read_geojson('map (3).geojson'))
    #
    # # TODO first celery task
    # zipped_path = dp_client.get_data(footprint=fp)
    # # zipped_path = "S2A_MSIL2A_20220601T080611_N0400_R078_T39VVG_20220601T120411.zip"
    # unzip_files(path_to_zip=zipped_path)

    # TODO second celery task
    # штука, которая достает r10_path для красной
    provider = SciHubSatelliteDataExtractor(path_to_data="data")

    # print(provider.extract_nir_image_path())
    # r10_path = 'data/S2A_MSIL2A_20220601T080611_N0400_R078_T39VVG_20220601T120411.SAFE/GRANULE/' \
    #       'L2A_T39VVG_A036254_20220601T081244/IMG_DATA/R10m'
    #
    # calculate_nvdi(path_to_data=r10_path)
