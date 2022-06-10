import logging

from geojson_pydantic import FeatureCollection

from . import models
from .database_config import SessionLocal

logger = logging.getLogger()


class Status:
    FIELD_CREATED = "FIELD_CREATED"

    STARTED_DOWNLOAD = "STARTED_DOWNLOAD"
    FINISHED_DOWNLOAD = "FINISHED_DOWNLOAD"
    ERROR_DOWNLOAD = "ERROR_DOWNLOAD"

    STARTED_CALCULATION = "STARTED_CALCULATION"
    FINISHED_CALCULATION = "FINISHED_CALCULATION"
    ERROR_CALCULATION = "ERROR_CALCULATION"


class CRUD:
    """
    This class is responsible for communicating with database.
    """

    def __init__(self):
        self.db = SessionLocal()

    def create_field(self, field: FeatureCollection):
        """
        Function that creates row in field table.
        :param field: field information from GeoJSON
        :return int field_id: field id from database
        """

        # Creating product ID and URL model.
        db_field = models.Fields(**{"geo_json": field.dict()},
                                 status=Status.FIELD_CREATED)

        logger.info("Adding field to database.")
        self.db.add(db_field)

        # Committing database changes.
        self.db.commit()

        # Refreshing product ID and URL model.
        self.db.refresh(db_field)

        # Save field id
        field_id = db_field.id

        self.db.close()
        return field_id

    def get_geojson_by_field_id(self, field_id: int):
        """
        Function that get information from geo_json column by field_id.
        :param int field_id: id of the field from user
        :return dict data.geo_json: information from geo_json column
        """

        logger.info(f"Getting GeoJSON by {field_id}.")
        # Getting JSON by fields id.
        data = self.db.query(models.Fields).filter_by(id=field_id).first()

        self.db.close()
        return data.geo_json

    def save_ndvi_path_to_db(self, path: str, field_id: int):
        """
        Saves path to NDVI image file to database.
        """

        logger.info(f"Updating {field_id} NDVI {path} column to db.")
        # Add NDVI path to db.
        self.db.query(models.Fields).where(
            models.Fields.id == field_id).update(
            {"ndvi": path})

        # Committing database changes.
        self.db.commit()

        self.db.close()

    def delete_field_data_from_db(self, field_id: int):
        """
        Deletes all data about the field under field_id.
        :param int field_id: id of the field from user
        """

        logger.info(f"Deleting {field_id} from db.")
        self.db.query(models.Fields).filter(
            models.Fields.id == field_id).delete()

        self.db.close()

    def change_status(self, field_id: int, status_text: str):
        """
        Changes status of the server process in the database.
        :param int field_id: id of the field from user
        :param str status_text: status text
        """

        logger.info(f"Updating {field_id} status column with {status_text}.")
        self.db.query(models.Fields).where(
            models.Fields.id == field_id).update({"status": status_text})

        # Committing database changes.
        self.db.commit()

        self.db.close()

    def get_status(self, field_id: int):
        """
        Gets and returns status of the server process in the database.
        :param int field_id: id of the field from user
        :return str data.status: status text
        """

        logger.info(f"Getting {field_id} status.")

        data = self.db.query(models.Fields).filter_by(id=field_id).first()
        return data.status
