import logging

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from backend.app.celery_tasks import count_ndvi, get_satellite_data
from backend.app.database import crud, schemas
from backend.app.file_system_storage import FileSystemStorage

from .routers_config import connecting_to_db

router = APIRouter(
    prefix="/field",
    tags=["field"],
    )

logger = logging.getLogger()


@router.post("/add")
def add_field(field: schemas.FieldCreate,
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

    return field_id


@router.get("/satellite_image")
def get_satellite_image(field_id: int,
                        conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Accepts field id and gets satellite data.
    :param int field_id: id of the field from user
    :param conn:
    :return:
    """

    logger.info(f"Accepted {field_id} to get satellite image.")

    # Get geojson by prod_id
    geo_json = conn.get_geojson_by_field_id(field_id)

    get_satellite_data(geo_json)

    # Getting info about products to which user is subscribed.
    logger.info(f"Got {field_id} satellite image.")

    conn.change_status(field_id, "Received")


@router.get("/calculate_ndvi")
def calculate_ndvi(field_id: int,
                   conn: crud.CRUD = Depends(connecting_to_db)):
    """
    Calculates NDVI and saves path to NDVI image to database.
    :param int field_id: id of the field from user
    :param conn:
    :return:
    """

    # Calculate NDVI and create NDVI image.
    count_ndvi(field_id)

    # Create path to the NDVI file.
    path = str(field_id) + 'NDVI.tif'

    # Save path to NDVI image to database.
    conn.save_ndvi_path_to_db(path=path, field_id=field_id)


@router.get("/ndvi_image")
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
    if status == "Ready":
        file_path = FileSystemStorage(field_id).get_ndvi_image()
        return FileResponse(path=file_path)

    return status


@router.delete("/delete")
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
    # Getting info about products to which user is subscribed.
    logger.info(f"Deleted {field_id} from db.")
