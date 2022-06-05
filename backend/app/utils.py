def unzip_files(path_to_zip, output_folder="unzipped_satellite_date"):
    # unzip
    import zipfile
    with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    return output_folder
