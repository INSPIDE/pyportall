import pandas as pd

from pyportall.api.engine.geopandas import GeocodingHelper
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.exceptions import PreFlightException


def test_geocoding(mocker, mocked, preflight_client):
    if mocked is True:
        mocker.patch.object(preflight_client, "call_indicators", side_effect=PreFlightException(2))

    geocoding_data = {
        "street": ["Gran Vía 46", "Calle Alcalá 10"],
        "city": ["Madrid", "Madrid"]
    }

    addresses = pd.DataFrame(geocoding_data)

    geocoding_helper = GeocodingHelper(preflight_client)

    try:
        geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))
    except PreFlightException as e:
        assert e.credits == 2
    else:
        raise AssertionError
