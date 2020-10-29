import pandas as pd

from pyportall.api.engine.geopandas import GeocodingHelper
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.engine.geopandas import GeocodingHelper, IndicatorHelper
from pyportall.api.models.indicators import DayOfWeek, Indicator, Moment, Month


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
    resolved_indicators = indicator_helper.resolve_aggregated(isovists, indicator=Indicator(code="pop"), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))

    assert resolved_indicators.size == 14
