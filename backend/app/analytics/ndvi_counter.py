import rasterio
import rasterio.mask
from geopandas import GeoDataFrame

from backend.app.fs.image_saver import ImageSaverToFileSystem


def calculate_and_save_ndvi_image(nir, red, file_path, field_geojson):
    """
    Calculates NDVI, creates NDVI image and saves to file system.
    Formula:
    NDVI = nir - red /(nir + red)
    :return:
    """

    # Transform coordinates
    field_geo = GeoDataFrame.from_features(
        field_geojson['features'], crs="EPSG:4326")
    n_reserve_proj = field_geo.to_crs(epsg=32637)

    # Open and crop b4 and b8
    with rasterio.open(red) as src:
        out_image_red, out_transform_red = rasterio.mask.mask(
            src, n_reserve_proj.geometry, crop=True)
        out_meta_red = src.meta.copy()
        out_meta_red.update({"driver": "GTiff",
                             "height": out_image_red.shape[1],
                             "width": out_image_red.shape[2],
                             "transform": out_transform_red})

    with rasterio.open(nir) as src:
        out_image_nir, out_transform_nir = rasterio.mask.mask(
            src, n_reserve_proj.geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_image_nir.shape[1],
                         "width": out_image_nir.shape[2],
                         "transform": out_transform_nir})

    # Open one of the images for meta
    b4 = rasterio.open(red)

    nir = out_image_nir
    red = out_image_red

    # Calculate ndvi
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

    # Write the NDVI image
    meta = b4.meta
    meta.update(driver='GTiff')
    meta.update(dtype=rasterio.float32)

    ImageSaverToFileSystem().save_ndvi_image(meta, ndvi, file_path=file_path)
