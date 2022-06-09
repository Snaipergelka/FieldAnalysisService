import rasterio


class ImageSaverToFileSystem:
    """
    This class is responsible for saving NDVI images to file system.
    It can be extended in case other image formats e.g. jpeg
    """

    def __init__(self):
        pass

    def save_ndvi_image(self, meta, ndvi,
                        file_path: str):
        """
        Writes image into a file and saves it in file system.
        You provide either file_path or (file_type and file_name)

        :param file_path:
        :param meta: meta of the field
        :param ndvi: calculated NDVI
        :param str file_type: file type of the image
        :param str file_name: file name of the image
        :return:
        """
        # TODO should check which args are provided
        with rasterio.open(file_path, 'w', **meta) as file:
            file.write(ndvi.astype(rasterio.float32))
