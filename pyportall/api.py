import os
import httpx
from typing import Any, Dict, Optional
from time import sleep

from .exceptions import PyPortallException


BATCH_DELAY_S = 5

ENDPOINT_METADATA = os.getenv("ENDPOINT_METADATA", "https://portall-api.inspide.com/v0/metadata/indicators/")
ENDPOINT_POLYGONS = os.getenv("ENDPOINT_POLYGONS", "https://portall-api.inspide.com/v0/indicators/polygons.json")
ENDPOINT_GEOCODING = os.getenv("ENDPOINT_GEOCODING", "https://portall-api.inspide.com/v0/tools/geocoding.json")
ENDPOINT_RESOLVE_ISOVISTS = os.getenv("ENDPOINT_RESOLVE_ISOVISTS", "https://portall-api.inspide.com/v0/tools/isovists.json")
ENDPOINT_RESOLVE_ISOLINES = os.getenv("ENDPOINT_RESOLVE_ISOLINES", "https://portall-api.inspide.com/v0/tools/isolines.json")


class APIClient:
    def __init__(self, api_key: Optional[str] = None, batch: bool = False) -> None:
        self.api_key = api_key or os.getenv("API_KEY")
        if self.api_key is None:
            raise PyPortallException("API key is required to use Portall's API")
        self.batch = batch

    def call(self, url: str, input: Any, preflight: bool = False, batch: bool = False) -> Any:
        query_params: Dict[str, Any] = {"apikey": self.api_key}
        if preflight is True:
            query_params["preflight"] = True
        if batch is True:
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
        else:
            raise PyPortallException(response.json())
