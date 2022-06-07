import rasterio


class FileSystemStorage:
    """
    This class is responsible for saving NDVI images to file system
    and getting file path to NDVI path.
    """

    def __init__(self, field_id):
        self.field_id = field_id

    def save_ndvi_image(self, meta, ndvi,
                        file_type: str = '.tif',
                        file_name: str = 'NDVI'):
        """
        Writes image into a file and saves it in file system.
        :param meta: meta of the field
        :param ndvi: calculated NDVI
        :param str file_type: file type of the image
        :param str file_name: file name of the image
        :return:
        """

        with rasterio.open(str(self.field_id) + file_name + file_type,
                           'w', **meta) as file:
            file.write(ndvi.astype(rasterio.float32))

    def get_ndvi_image(self,
                       directory_path: str = 'backend/app/',
                       file_type: str = '.tif',
                       file_name: str = 'NDVI'):
        """
        Forms path to image.
        :param directory_path: path to the directory where image is
        :param str file_type: file type of the image
        :param str file_name: file name of the image
        :return:
        """
        return directory_path + str(self.field_id) + file_name + file_type
