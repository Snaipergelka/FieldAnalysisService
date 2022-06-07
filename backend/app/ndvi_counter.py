import rasterio

from backend.app.file_system_storage import FileSystemStorage


def calculate_nvdi(nir, red, field_id: str):
    """
    Calculates NDVI, creates NDVI image and saves to file system.
    Formula: NDVI = nir - red /(nir + red)
    :return:
    """

    # Open b4 and b8
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

    FileSystemStorage(field_id).save_ndvi_image(meta, ndvi)
