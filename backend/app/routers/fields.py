import logging
import os
import shutil

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
from geojson_pydantic import FeatureCollection

from backend.app.celery_tasks import count_ndvi, get_satellite_data
from backend.app.database import crud, schemas
from backend.app.fs.file_system_storage import ArtifactsFileSystemStorage

from .routers_config import connecting_to_db

router = APIRouter(
    prefix="/field",
    tags=["field"],
)

Status = crud.Status

storage = ArtifactsFileSystemStorage(
    base_path=os.getenv("FS_STORAGE_BASE_PATH",
                        default="STORAGE"))

logger = logging.getLogger()


@router.post("/")
def add_field(field: FeatureCollection,
              conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Accepts field information in GeoJSON format and adds
    field information to database. Return field_id
    :param GeoJSON field:
    :param conn:
    :return int field_id: id of the field from db
    """

    # Adding field row to db.
    logger.info(f"Accepted {field} to add to db.")
    field_id = conn.create_field(field)

    logger.info(f"Added {field} to db.")

    return JSONResponse({
        "field_id": field_id
    })


@router.delete("/")
def delete_field(field_id: int,
                 conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Deletes field row from database.
    :param int field_id: id of the field from user
    :param conn:
    :return:
    """

    logger.info(f"Accepted {field_id} to delete from db.")
    conn.delete_field_data_from_db(field_id)

    # deleted folders and files from disk
    shutil.rmtree(storage.get_path_to_field_base(field_id))

    logger.info(f"Deleted {field_id} from db.")


@router.post("/image")
def download_satellite_image(field_id: schemas.FieldID,
                             conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Accepts field id and gets satellite data.
    :param int field_id: id of the field from user
    :param conn:
    :return:
    """

    logger.info(f"Accepted {field_id.field_id} to get satellite image.")
    status = conn.get_status(field_id.field_id)
    if status != Status.FIELD_CREATED:
        return JSONResponse({
            "status": "OUT_OF_ORDER",
            "message": "Please ensure that you preserve correct order"
                       " of API calls."
        })

    # Get geojson by prod_id
    geo_json = conn.get_geojson_by_field_id(field_id.field_id)

    # Get satellite data
    get_satellite_data.delay(geo_json, field_id.field_id)

    logger.info(f"Got {field_id.field_id} satellite image.")
    return JSONResponse({
        "status": Status.STARTED_DOWNLOAD,
        "message": "Started satellite data download."
    })


@router.post("/ndvi")
def calculate_ndvi(field_id: schemas.FieldID,
                   conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Calculates NDVI and saves path to NDVI image to database.
    :param conn:
    :param int field_id: id of the field from user
    :return:
    """

    # Check if satellite data is ready
    status = conn.get_status(field_id.field_id)

    if status == Status.FINISHED_DOWNLOAD:
        # Calculate NDVI and create NDVI image.
        count_ndvi.delay(field_id.field_id)
        message = "Started ndvi calculation."
    elif status == Status.ERROR_DOWNLOAD:
        message = "Error happened during image download."
    elif status == Status.STARTED_DOWNLOAD:
        message = "Data is not downloaded yet."
    elif status == Status.STARTED_CALCULATION:
        message = "Calculation is in progress."
    else:
        status = "OUT_OF_ORDER"
        message = "Please ensure that you preserve correct order " \
                  "of API calls."

    return JSONResponse({
        "status": status,
        "message": message
    })


@router.get("/ndvi/image")
def get_ndvi_image(field_id: int,
                   conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Checks if NDVI image is ready and returns image or returns status.
    :param int field_id: id of the field from user
    :param conn:
    :return status|FileResponse:
    """

    logger.info(f"Checking status of field under {field_id}.")

    # Get status of the NDVI image calculating
    status = conn.get_status(field_id)

    # Check status if image is ready
    if status == Status.FINISHED_CALCULATION:
        file_path = storage.get_path_to_ndvi_image(field_id=field_id)
        return FileResponse(path=file_path)
    else:
        if status == Status.ERROR_CALCULATION:
            message = "Error happened during ndvi calculation."
        elif status == Status.STARTED_CALCULATION:
            message = "NDVI calculation is in progress."
        else:
            status = "OUT_OF_ORDER"
            message = "Please ensure that you preserve correct " \
                      "order of API calls."

        return JSONResponse({
            "status": status,
            "message": message
        })
