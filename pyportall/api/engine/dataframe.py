
import json
import httpx
import pandas as pd
from typing import List, Optional, Union
from pydantic.types import UUID4

from pyportall.utils import jsonable_encoder
from pyportall.api.engine.core import APIHelper, ENDPOINT_AGGREGATED_INDICATORS, ENDPOINT_DISAGGREGATED_INDICATORS, ENDPOINT_GEOCODING, ENDPOINT_RESOLVE_ISOLINES, ENDPOINT_RESOLVE_ISOVISTS, ENDPOINT_DATAFRAMES
from pyportall.api.models.dataframe import PortallDataFrame, PortallDataFrameAPI
from pyportall.api.models.indicators import Indicator, Moment


class PortallDataFrameHelper(APIHelper):
    """Help with Portall's DataFrame wrappers."""

    def all(self) -> List[PortallDataFrame]:
        """Get all the dataframes available in Portall's database.

        Returns:
            A list of DataFrame-compatible dataframes.
        """

        pdfs_api_json = self.client.get(ENDPOINT_DATAFRAMES)

        return [PortallDataFrame.from_api(PortallDataFrameAPI.parse_obj(pdf_api_json), self.client) for pdf_api_json in pdfs_api_json]

    def get(self, id: UUID4) -> Union[PortallDataFrame, None]:
        """Get just one of the dataframes available in Portall's database.

        Args:
            id: Id. of the dataframe to be retrieved.

        Returns:
            DataFrame-compatible dataframe.
        """
        endpoint = f"{ENDPOINT_DATAFRAMES}/{id}/"
        params = {}
        params["apikey"] = self.client.api_key
        headers = {}

        result = httpx.get(endpoint, params=params, headers=headers)
        
        body = result.json()

        df = pd.DataFrame(body['data'])

        portall_dataframe = PortallDataFrame.from_df(
            df,
            id=id,
            client=self.client, 
            name=body['name'],
            metadata=json.dumps(body['metadata']),
        )

        return portall_dataframe

        # return PortallDataFrame.from_api(PortallDataFrameAPI.parse_obj(pdf_api_json.json()), self.client)
