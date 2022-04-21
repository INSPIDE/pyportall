import os
import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import json

from pyportall.api.engine.core import APIClient


DUMMY_API_KEY = "dummy"


@pytest.fixture(scope="module")
def mocked():
    return os.getenv("PYPORTALL_API_KEY") is None


@pytest.fixture(scope="module")
def client():
    return APIClient(api_key=os.getenv("PYPORTALL_API_KEY", DUMMY_API_KEY))


@pytest.fixture(scope="module")
def preflight_client():
    return APIClient(api_key=os.getenv("PYPORTALL_API_KEY", DUMMY_API_KEY), preflight=True)


@pytest.fixture(scope="module")
def batch_client():
    return APIClient(api_key=os.getenv("PYPORTALL_API_KEY", DUMMY_API_KEY), batch=True)


### Don't take the samples below for valid ones!!! They're only meant to serve as test stubs.

@pytest.fixture(scope="module")
def geocodings():
    geocodings_dict = {
        'geometry': {
            0: Point(-3.70587, 40.42048),
            1: Point(-3.37825, 40.47281)
        },
        'country': {
            0: 'Spain',
            1: 'Spain'
        },
        'state': {
            0: None,
            1: None
        },
        'county': {
            0: None,
            1: None
        },
        'city': {
            0: 'Madrid',
            1: 'Madrid'
        },
        'district': {
            0: None,
            1: None
        },
        'postal_code': {
            0: None,
            1: None
        },
        'street': {
            0: 'Gran Vía 46',
            1: 'Calle Alcalá 10'
        }
    }

    return gpd.GeoDataFrame(geocodings_dict, crs="EPSG:4326")

@pytest.fixture(scope="module")
def isovists():
    isovists_dict = {
        'geometry': {
            0: Polygon([[-3.70587, 40.420874041], [-3.705860874, 40.420879569], [-3.705851483, 40.420885259], [-3.705841808, 40.42089112]]),
            1: Polygon([[-3.379755, 40.4738045], [-3.3796692, 40.4743195], [-3.3794975, 40.4748344], [-3.3791542, 40.4748344], [-3.379755, 40.4738045]])
        },
        'destination': {
            0: {'coordinates': [-3.70587, 40.42048], 'type': 'Point'},
            1: {'coordinates': [-3.37825, 40.47281], 'type': 'Point'}
        },
        'fov_deg': {
            0: 360,
            1: 360
        },
        'heading_deg': {
            0: 0,
            1: 0
        },
        'num_rays': {
            0: -1,
            1: -1
        },
        'radius_m': {
            0: 100,
            1: 100
        }
    }

    return gpd.GeoDataFrame(isovists_dict, crs="EPSG:4326")


@pytest.fixture(scope="module")
def isolines():
    isolines_dict = {
        'geometry': {
            0: Polygon([[-3.70587, 40.420874041], [-3.705860874, 40.420879569], [-3.705851483, 40.420885259], [-3.705841808, 40.42089112]]),
            1: Polygon([[-3.379755, 40.4738045], [-3.3796692, 40.4743195], [-3.3794975, 40.4748344], [-3.3791542, 40.4748344], [-3.379755, 40.4738045]])
        },
        'destination': {
            0: {'coordinates': [-3.70587, 40.42048], 'type': 'Point'},
            1: {'coordinates': [-3.37825, 40.47281], 'type': 'Point'}
        },
        'mode': {
            0: "pedestrian",
            1: "pedestrian"
        },
        'range': {
            0: 200,
            1: 200
        },
        'moment': {
            0: None,
            1: None
        }
    }

    return gpd.GeoDataFrame(isolines_dict, crs="EPSG:4326")


@pytest.fixture(scope="module")
def aggregated_indicators():
    aggregated_indicators_dict = {
        'geometry': {
            0: Polygon([[-3.70587, 40.420874041], [-3.705860874, 40.420879569], [-3.705851483, 40.420885259], [-3.705841808, 40.42089112]]),
            1: Polygon([[-3.379755, 40.4738045], [-3.3796692, 40.4743195], [-3.3794975, 40.4748344], [-3.3791542, 40.4748344], [-3.379755, 40.4738045]])
        },
        'destination': {
            0: {'coordinates': [-3.70587, 40.42048], 'type': 'Point'},
            1: {'coordinates': [-3.37825, 40.47281], 'type': 'Point'}
        },
        'fov_deg': {
            0: 360,
            1: 360
        },
        'heading_deg': {
            0: 0,
            1: 0
        },
        'num_rays': {
            0: -1,
            1: -1
        },
        'radius_m': {
            0: 100,
            1: 100
        },
        'values': {
            0: 123,
            1: 456
        }
    }

    return gpd.GeoDataFrame(aggregated_indicators_dict, crs="EPSG:4326")


@pytest.fixture(scope="module")
def disaggregated_indicators():
    disaggregated_indicators_dict = {
        "geometry": {
            0: Polygon([[-3.706061463, 40.420662223], [-3.706179014, 40.42062551], [-3.706195805, 40.420525091], [-3.706095045, 40.420461385], [-3.705977495, 40.420498098], [-3.705960704, 40.420598517], [-3.706061463, 40.420662223]]),
            1: Polygon([[-3.706061463, 40.420662223], [-3.706179014, 40.42062551], [-3.706195805, 40.420525091], [-3.706095045, 40.420461385], [-3.705977495, 40.420498098], [-3.705960704, 40.420598517], [-3.706061463, 40.420662223]]),
            2: Polygon([[-3.706061463, 40.420662223], [-3.706179014, 40.42062551], [-3.706195805, 40.420525091], [-3.706095045, 40.420461385], [-3.705977495, 40.420498098], [-3.705960704, 40.420598517], [-3.706061463, 40.420662223]]),
            3: Polygon([[-3.706061463, 40.420662223], [-3.706179014, 40.42062551], [-3.706195805, 40.420525091], [-3.706095045, 40.420461385], [-3.705977495, 40.420498098], [-3.705960704, 40.420598517], [-3.706061463, 40.420662223]]),
            4: Polygon([[-3.706061463, 40.420662223], [-3.706179014, 40.42062551], [-3.706195805, 40.420525091], [-3.706095045, 40.420461385], [-3.705977495, 40.420498098], [-3.705960704, 40.420598517], [-3.706061463, 40.420662223]]),
            5: Polygon([[-3.706061463, 40.420662223], [-3.706179014, 40.42062551], [-3.706195805, 40.420525091], [-3.706095045, 40.420461385], [-3.705977495, 40.420498098], [-3.705960704, 40.420598517], [-3.706061463, 40.420662223]])
        },
        "id": {
            0: 631507574769340927,
            1: 631507574769340927,
            2: 631507574769340927,
            3: 631507574769340927,
            4: 631507574769340927,
            5: 631507574769340927
        },
        "value": {
            0: 123,
            1: 345.67,
            2: 123,
            3: 345.67,
            4: 123,
            5: 345.67
        },
        "weight": {
            0: 1,
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1
        }
    }

    return gpd.GeoDataFrame(disaggregated_indicators_dict, crs="EPSG:4326")




@pytest.fixture(scope="module")
def dataframe_json_data():
    data = [
        {'Fecha': '2000-01-23', 'Impactos': 2345, 'Dwell time': 12.4},
        {'Fecha': '2000-01-24', 'Impactos': 3456, 'Dwell time': 11.3},
        {'Fecha': '2000-01-25', 'Impactos': 3423, 'Dwell time': 13.6},
        {'Fecha': '2000-01-26', 'Impactos': 3456, 'Dwell time': 12.2}
    ]

    return data


@pytest.fixture(scope="module")
def dataframe_json_edited_data():
    data = [
        {'Fecha': '2000-01-23', 'Impactos': 1123, 'Dwell time': 1.4},
        {'Fecha': '2000-01-24', 'Impactos': 2233, 'Dwell time': 1.3},
        {'Fecha': '2000-01-25', 'Impactos': 6677, 'Dwell time': 1.6},
        {'Fecha': '2000-01-26', 'Impactos': 6654, 'Dwell time': 1.2}
    ]

    return data 


@pytest.fixture(scope="module")
def saved_dataframe():

    data = [
        {'Fecha': '2000-01-23', 'Impactos': 2345, 'Dwell time': 12.4},
        {'Fecha': '2000-01-24', 'Impactos': 3456, 'Dwell time': 11.3},
        {'Fecha': '2000-01-25', 'Impactos': 3423, 'Dwell time': 13.6},
        {'Fecha': '2000-01-26', 'Impactos': 3456, 'Dwell time': 12.2}
    ]

    dataframe = {
        'id': '00614f81-81ce-4140-8e6d-d0a7c4f187d3',
        'name': 'dataframe 4',
        'description': '',
        'data_type': 'json',
        'data': data,
        'metadata': {'company': 23, 'component': '23423-f334r-34r34-34r34'}
    }

    return dataframe

