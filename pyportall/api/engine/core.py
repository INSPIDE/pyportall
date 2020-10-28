import os
import httpx
from typing import Any, Dict, Optional
from time import sleep

from pyportall.exceptions import PyPortallException


BATCH_DELAY_S = 5

ENDPOINT_METADATA = os.getenv("PYPORTALL_ENDPOINT_METADATA", "https://portall-api.inspide.com/v0/metadata/indicators/")
ENDPOINT_GEOCODING = os.getenv("PYPORTALL_ENDPOINT_GEOCODING", "https://portall-api.inspide.com/v0/pyportall/geocoding.geojson")
ENDPOINT_RESOLVE_ISOVISTS = os.getenv("PYPORTALL_ENDPOINT_RESOLVE_ISOVISTS", "https://portall-api.inspide.com/v0/pyportall/isovists.geojson")
ENDPOINT_RESOLVE_ISOLINES = os.getenv("PYPORTALL_ENDPOINT_RESOLVE_ISOLINES", "https://portall-api.inspide.com/v0/pyportall/isolines.geojson")
ENDPOINT_AGGREGATED_INDICATORS = os.getenv("PYPORTALL_ENDPOINT_AGGREGATED_INDICATORS", "https://portall-api.inspide.com/v0/pyportall/indicators.geojson")
ENDPOINT_DISAGGREGATED_INDICATORS = os.getenv("PYPORTALL_ENDPOINT_DISAGGREGATED_INDICATORS", "https://portall-api.inspide.com/v0/pyportall/indicator.geojson")


class APIClient:
    def __init__(self, api_key: Optional[str] = None, batch: Optional[bool] = False) -> None:
        self.api_key = api_key or os.getenv("PYPORTALL_API_KEY")
        if self.api_key is None:
            raise PyPortallException("API key is required to use Portall's API")
        self.batch = batch

    def call_indicators(self, url: str, input: Any, preflight: bool = False, batch: Optional[bool] = None) -> Any:
        query_params: Dict[str, Any] = {"apikey": self.api_key}
        if preflight is True:
            query_params["preflight"] = True
        if batch is True or (batch is None and self.batch is True):
            query_params["batch"] = True

        try:
            response = httpx.post(url, params=query_params, headers={"content-type": "application/json"}, json=input)
        except httpx.ReadTimeout:
            raise PyPortallException("API is timing out, please consider using a batch-enabled client")

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            job_url = response.json()["detail"]

            while True:
                response = httpx.get(job_url, params={"apikey": self.api_key})

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 202:
                    sleep(BATCH_DELAY_S)
                else:
                    return None
        elif response.status_code == 401:
            raise PyPortallException("Wrong API key")
        elif response.status_code == 422:
            raise PyPortallException(response.json()["detail"])
        else:
            raise PyPortallException(response.text)

    def call_metadata(self, url: str = ENDPOINT_METADATA) -> Any:
        response = httpx.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise PyPortallException(response.json())


class APIHelper:
    def __init__(self, client: APIClient) -> None:
        self.client = client
