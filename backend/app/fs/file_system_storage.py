import os
import pathlib

ZIPPED_FOLDER = "zipped"
UNZIPPED_FOLDER = "unzipped"
NDVI_IMAGE_DATA_FOLDER = "ndvi"
NDVI_IMAGE_FILE = "NDVI.tif"


class ArtifactsFileSystemStorage:
    """
    This class provides abstraction above file system. It stores all
    artifacts related to satellite data and analytics of them.
    Usually it doesn't save artifacts by itself
    but provides a path where it should be saved to.

    Used format:
        base_path/
            field_id/
                ZIPPED_FOLDER/
                UNZIPPED_FOLDER/
                NDVI_IMAGE_DATA_FOLDER/
    """

    def __init__(self, base_path):
        self.base_path = base_path

    def __create_if_not_exist(self, field_id, data_type=""):
        try:
            pathlib.Path(os.path.join(
                self.base_path, str(field_id), data_type)
            ).mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            return

    def get_path_to_satellite_data_zipped(self, field_id):
        self.__create_if_not_exist(field_id=field_id, data_type=ZIPPED_FOLDER)
        return os.path.join(self.base_path, str(field_id), ZIPPED_FOLDER)

    def get_path_to_satellite_data_unzipped(self, field_id):
        self.__create_if_not_exist(field_id=field_id,
                                   data_type=UNZIPPED_FOLDER)
        return os.path.join(self.base_path, str(field_id), UNZIPPED_FOLDER)

    def get_path_to_ndvi_image(self, field_id):
        self.__create_if_not_exist(field_id=field_id,
                                   data_type=NDVI_IMAGE_DATA_FOLDER)
        return os.path.join(self.base_path,
                            str(field_id),
                            NDVI_IMAGE_DATA_FOLDER,
                            NDVI_IMAGE_FILE)

    def get_path_to_field_base(self, field_id):
        self.__create_if_not_exist(field_id)
        return os.path.join(
            self.base_path,
            str(field_id))
