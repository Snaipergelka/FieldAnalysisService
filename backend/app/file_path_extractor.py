import os


class SciHubSatelliteDataExtractor:
    """
    This class is responsible for parsing data and files structure
    received from SciHub site.
    The problem is that directories and files have dynamic names based on date.
    Example:
    'data/
    S2A_MSIL2A_20220601T080611_N0400_R078_T39VVG_20220601T120411.SAFE/
    GRANULE/L2A_T39VVG_A036254_20220601T081244/IMG_DATA/R10m'
    """

    def __init__(self, path_to_data):
        self.path = path_to_data

    def __extract_base_path(self, resolution: str):
        """
        Extracts base path for NIR and Red files.
        :param str resolution: resolution of image R10m|R20m|R30m
        :return:
        """

        res = [p for p in os.walk(self.path)
               if "GRANULE" in p[0]
               and "IMG_DATA" in p[0]
               and resolution in p[0]]

        if len(res) == 0:
            raise Exception(
                "Impossible to parse provided folder. "
                "Please check if path is correct!"
            )

        return res[0]

    def extract_nir_image_path(self, resolution: str = 'R10m'):
        """
        Extracts path to NIR image.
        :param str resolution: resolution of image R10m|R20m|R30m
        :return str path: path to the NIR image
        """
        bp = self.__extract_base_path(resolution)
        nir = [p for p in bp[2] if "B08" in p][0]
        return os.path.join(bp[0], nir)

    def extract_red_image_path(self, resolution: str = 'R10m'):
        """
        Extracts path to Red image.
        :param str resolution: resolution of image R10m|R20m|R30m
        :return str path: path to the Red image
        """
        bp = self.__extract_base_path(resolution)
        red = [p for p in bp[2] if "B04" in p][0]
        return os.path.join(bp[0], red)
