import json

import rasterio
from rasterio import mask

from backend.app.fs.image_saver import ImageSaverToFileSystem


def calculate_and_save_ndvi_image(nir, red, file_path):
    """
    Calculates NDVI, creates NDVI image and saves to file system.
    Formula: NDVI = subscription-manager repos --enable=rhel-7-server-extras-rpmsnir - red /(nir + red)
    :return:
    """

    # field_geo = json.load(open(field_geo))
    # # Open and crop b4 and b8
    # with rasterio.open(red) as src:
    #     out_image, out_transform = rasterio.mask.mask(src, field_geo['features'][0]['geometry'], crop=True)
    #     out_meta = src.meta.copy()
    #     out_meta.update({"driver": "GTiff",
    #                      "height": out_image.shape[1],
    #                      "width": out_image.shape[2],
    #                      "transform": out_transform})
    #
    # with rasterio.open(nir) as src:
    #     out_image, out_transform = rasterio.mask.mask(src, field_geo['features'][0]['geometry'], crop=True)
    #     out_meta = src.meta.copy()
    #     out_meta.update({"driver": "GTiff",
    #                      "height": out_image.shape[1],
    #                      "width": out_image.shape[2],
    #                      "transform": out_transform})

    b4 = rasterio.open(red)
    b8 = rasterio.open(nir)

    # read Red(b4) and NIR(b8) as arrays
    red = b4.read()
    nir = b8.read()

    # Calculate ndvi
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

    # Write the NDVI image
    meta = b4.meta
    meta.update(driver='GTiff')
    meta.update(dtype=rasterio.float32)

    ImageSaverToFileSystem().save_ndvi_image(meta, ndvi, file_path=file_path)
