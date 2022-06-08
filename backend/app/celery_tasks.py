import logging
import os
import shutil

from celery import Celery
from sentinelsat import SentinelAPI, geojson_to_wkt

from backend.app.analytics.ndvi_counter import calculate_and_save_ndvi_image
from backend.app.database.crud import CRUD
from backend.app.fs.file_system_storage import ArtifactsFileSystemStorage
from backend.app.satellite_data_providers.satellite_data_client import SatelliteDataClient
from backend.app.satellite_data_providers.satellite_data_extractor import SciHubSatelliteDataExtractor
from backend.app.utils import unzip_files


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - "
           "[%(levelname)s] - "
           "%(name)s - "
           "(%(filename)s).%(funcName)s(%(lineno)d) - "
           "%(message)s",
)

app = Celery('get_information',
             broker=os.environ.get('BROKER_URL'))

api = SentinelAPI(os.environ.get("USER"),
                  os.environ.get("PASSWORD"),
                  'https://apihub.copernicus.eu/apihub')

dp_client = SatelliteDataClient(api_client=api)
crud = CRUD()
storage = ArtifactsFileSystemStorage(base_path=os.getenv("FS_STORAGE_BASE_PATH", default="STORAGE"))


@app.task()
def get_satellite_data(geo_json: dict, field_id: int):
    """
    Gets field data from api,
    takes zipped data and
    unzips it.
    :param field_id:
    :param dict geo_json:
    :return str zipped_path:
    """
    # Convert a GeoJSON object to Well-Known Text
    footprint = geojson_to_wkt(geo_json)
    zipped_folder = storage.get_path_to_satellite_data_zipped(field_id)

    # Get data from footprint and return path to zipped data
    # TODO check on exception, particularly UnAuthorized
    zipped_path = dp_client.get_data(footprint=footprint, output_folder=zipped_folder)

    # Unzip directory and return path to it
    unzip_files(path_to_zip=zipped_path, output_folder=storage.get_path_to_satellite_data_unzipped(field_id))
    # Delete zipped data
    shutil.rmtree(zipped_folder)

    # Change status
    crud.change_status(field_id, "Received")


@app.task()
def count_ndvi(field_id: int):
    """
    Calculates NDVI and creates NDVI image for field
    under field_id provided by api.
    :param int field_id: id provide by api
    :return:
    """

    # Get path to the unzipped satellite data
    path = storage.get_path_to_satellite_data_unzipped(field_id)

    # Get path to Red and NIR satellite images
    provider = SciHubSatelliteDataExtractor(path_to_data=path)
    nir = provider.extract_nir_image_path()
    red = provider.extract_red_image_path()

    # Create path to the NDVI file.
    ndvi_folder_path = storage.get_path_to_ndvi_image(field_id=field_id)
    file_path = os.path.join(ndvi_folder_path, 'NDVI.tif')

    logging.info(f"Started ndvi calculation! nir:{nir} red:{red} out: {file_path}")
    # TODO мы иногда получаем очень большой снимок, нужно видимо обрезать
    calculate_and_save_ndvi_image(nir=nir, red=red, file_path=file_path)

    # Save path to NDVI image to database.
    # It is used when we return image from endpoint
    crud.save_ndvi_path_to_db(path=file_path, field_id=field_id)


if __name__ == "__main__":
    argv = [
        'worker',
        '--loglevel=INFO',
        '-E'
    ]
    app.worker_main(argv)
