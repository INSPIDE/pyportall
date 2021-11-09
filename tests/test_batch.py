import pandas as pd

from pyportall.api.engine.geopandas import GeocodingHelper
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.engine.geopandas import GeocodingHelper, IndicatorHelper
from pyportall.api.models.indicators import Day, Indicator, Moment, Month


def test_geocoding(mocked, batch_client):
    if mocked is True:
        raise AssertionError("Batch tests need a real API key.")

    geocoding_data = {
        "street": ["Gran Vía 46", "Calle Alcalá 10"],
        "city": ["Madrid", "Madrid"]
    }

    addresses = pd.DataFrame(geocoding_data)

    geocoding_helper = GeocodingHelper(batch_client)
    resolved_geocodings = geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))

    assert resolved_geocodings.size == 16


def test_aggregated_indicators(mocked, batch_client, isovists):
    if mocked is True:
        raise AssertionError("Batch tests need a real API key.")

    indicator_helper = IndicatorHelper(batch_client)
    resolved_indicators = indicator_helper.resolve_aggregated(isovists, indicator=Indicator(code="pop_res"), moment=Moment(day=Day(8), month=Month.february, hour=15, year=2021))

    assert resolved_indicators.size == 14
