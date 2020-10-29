import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

from pyportall.api.engine.geopandas import GeocodingHelper
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.models.lbs import GeocodingOptions, IsovistOptions
from pyportall.api.engine.geopandas import GeocodingHelper, IsolineHelper, IsovistHelper, IndicatorHelper
from pyportall.api.models.indicators import DayOfWeek, Indicator, Moment, Month


def test_geocoding(mocker, mocked, client, geocodings):
    if mocked is True:
        mocker.patch.object(client, "call_indicators", return_value=geocodings)

    geocoding_data = {
        "street": ["Gran Vía 46", "Calle Alcalá 10"],
        "city": ["Madrid", "Madrid"]
    }

    addresses = pd.DataFrame(geocoding_data)

    geocoding_helper = GeocodingHelper(client)
    resolved_geocodings = geocoding_helper.resolve(addresses, options=GeocodingOptions(country="Spain"))

    assert resolved_geocodings.size == 16


def test_isovists(mocker, mocked, client, isovists):
    if mocked is True:
        mocker.patch.object(client, "call_indicators", return_value=isovists)

    isovist_data = {
        "geometry": [Point(-3.70587, 40.42048), Point(-3.37825, 40.47281)]
    }

    isovists_gdf = gpd.GeoDataFrame(isovist_data, crs="EPSG:4326")

    isovist_helper = IsovistHelper(client)
    resolved_isovists = isovist_helper.resolve(isovists_gdf, options=IsovistOptions(radius_m=100))

    assert resolved_isovists.size == 12


def test_isolines(mocker, mocked, client, isolines):
    if mocked is True:
        mocker.patch.object(client, "call_indicators", return_value=isolines)

    isoline_data = {
        "geometry": [Point(-3.70587, 40.42048), Point(-3.37825, 40.47281)],
        "mode": "pedestrian",
        "range_s": 200
    }

    isolines_gdf = gpd.GeoDataFrame(isoline_data, crs="EPSG:4326")

    isoline_helper = IsolineHelper(client)
    resolved_isolines = isoline_helper.resolve(isolines_gdf)

    assert resolved_isolines.size == 10


def test_aggregated_indicators(mocker, mocked, client, isovists, aggregated_indicators):
    if mocked is True:
        mocker.patch.object(client, "call_indicators", return_value=aggregated_indicators)

    indicator_helper = IndicatorHelper(client)
    resolved_indicators = indicator_helper.resolve_aggregated(isovists, indicator=Indicator(code="pop"), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))

    assert resolved_indicators.size == 14


def test_disaggregated_indicator(mocker, mocked, client, disaggregated_indicators):
    if mocked is True:
        mocker.patch.object(client, "call_indicators", return_value=disaggregated_indicators)

    indicator_helper = IndicatorHelper(client)
    resolved_indicators = indicator_helper.resolve_disaggregated(Polygon([[-3.379755, 40.4738045], [-3.3796692, 40.4743195], [-3.3794975, 40.4748344], [-3.3791542, 40.4748344], [-3.379755, 40.4738045]]), indicator=Indicator(code="pop", aggregated=False), moment=Moment(dow=DayOfWeek.monday, month=Month.february, hour=15))

    assert resolved_indicators.size == 24
