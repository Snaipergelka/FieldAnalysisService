import os


class SatelliteDataClient:
    def __init__(self, api_client):
        self.client = api_client

    def get_data(self,
                 footprint,
                 output_folder: str = "satellite_data_providers"):
        """
        Gets data from Copernicus open access hub api by footprint.

        :param footprint: information about field
        :param str output_folder: folder where satellite data stores
        :return: path to zipped data
        """

        # search by polygon, time, and SciHub query keywords
        products = self.client.query(footprint,
                                     date=('20220101', '20220605'),
                                     platformname='Sentinel-2',
                                     cloudcoverpercentage=(0, 10))

        # convert to Pandas DataFrame
        products_df = self.client.to_dataframe(products)

        # sort and limit to first best product
        products_df_sorted = products_df.sort_values(
            ['cloudcoverpercentage', 'ingestiondate'],
            ascending=[True, True]
        )
        products_df_sorted = products_df_sorted.iloc[0]
        title = products_df_sorted['title']
        m_uuid = products_df_sorted['uuid']

        # download best results from the search
        self.client.download(id=m_uuid, directory_path=output_folder)

        # return path to downloaded data
        return os.path.join(output_folder, title + ".zip")
