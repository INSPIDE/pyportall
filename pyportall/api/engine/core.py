"""Module where core API-related classes live."""

import os
import httpx
from typing import Any, Dict, Optional
from time import sleep

from pyportall.exceptions import AuthError, BatchError, PreFlightException, PyPortallException, RateLimitError, TimeoutError, ValidationError
from pyportall.api.models.preflight import Preflight


BATCH_DELAY_S = 5

ENDPOINT_METADATA = os.getenv("PYPORTALL_ENDPOINT_METADATA", "https://portall-api.inspide.com/v0/metadata/indicators/")
ENDPOINT_GEOCODING = os.getenv("PYPORTALL_ENDPOINT_GEOCODING", "https://portall-api.inspide.com/v0/pyportall/geocoding.geojson")
ENDPOINT_RESOLVE_ISOVISTS = os.getenv("PYPORTALL_ENDPOINT_RESOLVE_ISOVISTS", "https://portall-api.inspide.com/v0/pyportall/isovists.geojson")
ENDPOINT_RESOLVE_ISOLINES = os.getenv("PYPORTALL_ENDPOINT_RESOLVE_ISOLINES", "https://portall-api.inspide.com/v0/pyportall/isolines.geojson")
ENDPOINT_AGGREGATED_INDICATORS = os.getenv("PYPORTALL_ENDPOINT_AGGREGATED_INDICATORS", "https://portall-api.inspide.com/v0/pyportall/indicators.geojson")
ENDPOINT_DISAGGREGATED_INDICATORS = os.getenv("PYPORTALL_ENDPOINT_DISAGGREGATED_INDICATORS", "https://portall-api.inspide.com/v0/pyportall/indicator.geojson")


class APIClient:
    """This class holds the direct interface to Portall's API. Other classes may need to use one API client to actually send requests to the API."""

    def __init__(self, api_key: Optional[str] = None, batch: Optional[bool] = False, preflight: Optional[bool] = False) -> None:
        """When instantiating an API client, you will provide an API key and optionally opt for batch or preflight modes.

        In preflight mode, requests to the API will not be executed. Instead, the API returns the estimated cost in credits for such request.

        Use batch mode when requests take longer to execute than the default API timeout (around 15s).

        Args:
            api_key: API key to use with Portall's API, in case no API key is available via the `PYPORTALL_API_KEY` environment variable. Please contact us if you need one.
            batch: Whether the client will work in batch mode or not.
            preflight: Whether the client will work in preflight mode or not.

        Raises:
            PyPortallException: Raised if no API key is available either through the `api_key` parameter or the `PYPORTALL_API_KEY` environment variable.
        """
        self.api_key = api_key or os.getenv("PYPORTALL_API_KEY")
        if self.api_key is None:
            raise PyPortallException("API key is required to use Portall's API")
        self.batch = batch
        self.preflight = preflight

    def call_indicators(self, url: str, input: Any) -> Any:
        """Send requests to Portall's indicator API.

        Takes an arbitrary object and, as long as it can be transformed into a JSON string, sends it to the indicator API. It deals with preflight and batch mode according to the settings defined upon creation of the client.

        Args:
            url: URL of the specific API endpoint in question.
            input: Any python object that can be encoded to a JSON string.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            AuthError: Authentication has failed, probably because of a wrong API key.
            BatchError: A batch request has failed, because of an error or because the batch timeout has expired.
            PreFlightException: Raised in preflight mode, includes the number of estimated credits that the actual request would consume.
            PyPortallException: Generic API exception.
            RateLimitError: The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded.
            TimeoutError: A regular (non-batch) request has timed out.
            ValidationError: The format of the request is not valid.
        """

        query_params: Dict[str, Any] = {"apikey": self.api_key}
        if self.preflight is True:
            query_params["preflight"] = True
        if self.batch is True:
            query_params["batch"] = True

        try:
            response = httpx.post(url, params=query_params, headers={"content-type": "application/json"}, json=input)
        except httpx.ReadTimeout:
            raise TimeoutError("API is timing out, please consider using a batch-enabled client")

        if response.status_code == 200:
            if self.preflight:
                raise PreFlightException(Preflight(**response.json()).detail)
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
                    raise BatchError("Batch job is not available, probably because of an error or because the batch timeout has expired")
        elif response.status_code == 401:
            raise AuthError("Wrong API key")
        elif response.status_code == 422:
            raise ValidationError(response.json()["detail"])
        elif response.status_code == 429:
            raise RateLimitError(response.json()["detail"])
        else:
            raise PyPortallException(response.text)

    def call_metadata(self) -> Any:
        """Send requests to Portall's metadata API.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            PyPortallException: Generic API exception.
        """

        response = httpx.get(ENDPOINT_METADATA, params={"apikey": self.api_key})

        if response.status_code == 200:
            return response.json()
        else:
            raise PyPortallException(response.json())


class APIHelper:
    """Ensure a common structure for helpers that actually do things."""

    def __init__(self, client: APIClient) -> None:
        """Class constructor to attach the coresponding API client.

        Args:
            client: API client object that the helper will use to actually send requests to the API when it has to.
        """
        self.client = client
