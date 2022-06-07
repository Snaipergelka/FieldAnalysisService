import os

from celery import Celery
from sentinelsat import SentinelAPI, geojson_to_wkt

from backend.app.file_path_extractor import SciHubSatelliteDataExtractor
from backend.app.ndvi_counter import calculate_nvdi
from backend.app.satellite_image_provider import SatelliteDataProvider
from backend.app.utils import unzip_files

app = Celery('get_information',
             broker=os.environ.get('BROKER_URL'))

api = SentinelAPI(os.environ.get("USER"),
                  os.environ.get("PASSWORD"),
                  'https://apihub.copernicus.eu/apihub')

dp_client = SatelliteDataProvider(api_client=api)


@app.task()
def get_satellite_data(geo_json: dict):
    """
    Gets field data from api,
    takes zipped data and
    unzips it.
    :param dict geo_json:
    :return str zipped_path:
    """

    # Convert a GeoJSON object to Well-Known Text
    footprint = geojson_to_wkt(geo_json)

    # Get data from footprint and return path to zipped data
    zipped_path = dp_client.get_data(footprint=footprint)

    # Unzip directory and return path to it
    unzip_files(path_to_zip=zipped_path)


@app.task()
def count_ndvi(field_id: int):
    """
    Calculates NDVI and creates NDVI image for field
    under field_id provided by api.
    :param int field_id: id provide by api
    :return:
    """
    provider = SciHubSatelliteDataExtractor(path_to_data="data")
    nir = provider.extract_nir_image_path()
    red = provider.extract_red_image_path()
    calculate_nvdi(nir=nir, red=red,
                   field_id=str(field_id))


if __name__ == "__main__":
    argv = [
        'worker',
        '--loglevel=INFO',
        '-E'
    ]
    app.worker_main(argv)
