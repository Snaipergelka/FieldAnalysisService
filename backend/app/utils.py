import zipfile


def unzip_files(path_to_zip: str,
                output_folder: str = "unzipped_satellite_date"):
    """
    Unzip file with satellite data about the field.
    :param str path_to_zip: path to zipped directory
    :param str output_folder: path to folder where save unzipped directory
    :return str output_folder: path to unzipped folder
    """

    # unzip file
    with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    return output_folder
