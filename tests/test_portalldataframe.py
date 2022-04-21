import pandas as pd
import json
from uuid import UUID

from pyportall.api.models.dataframe import PortallDataFrame
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.models.lbs import GeocodingOptions, IsovistOptions
from pyportall.api.engine.geopandas import GeocodingHelper, IsolineHelper, IsovistHelper, IndicatorHelper
from pyportall.api.models.indicators import Day, Indicator, Moment, Month
from pyportall.api.engine.dataframe import PortallDataFrameHelper

def test_dataframe_from_df(mocker, mocked, client, saved_dataframe, dataframe_json_data):
    """ Test the method from_df that creates a PortallDataframe from a pandas DataFrame"""

    if mocked is True:
        mocker.patch.object(client, "post", return_value=saved_dataframe)

    # create a pandas example dataframe and a json metadata example
    dataframe = pd.DataFrame(dataframe_json_data)
    metadata = '{"company":23, "component":"23423-f334r-34r34-34r34"}'

    # create an instance of PortallDataFrame with client 
    portall_df = PortallDataFrame.from_df(
        dataframe,
        client=client, 
        name="New dataframe",
        description="This is the description",
        metadata=metadata
    )

    
    assert portall_df.name == "New dataframe"


def test_dataframe_new(mocker, mocked, client, saved_dataframe, dataframe_json_data):

    if mocked is True:
        mocker.patch.object(client, "post", return_value=saved_dataframe)

    dataframe = pd.DataFrame(dataframe_json_data)
    metadata = '{"company":23, "component":"23423-f334r-34r34-34r34"}'

    portall_df = PortallDataFrame.from_df(
        dataframe, 
        client=client, 
        name="New dataframe",
        metadata=metadata,
    )

    result = portall_df.save()

    assert UUID(result['id'])

def test_dataframe_update(mocker, mocked, client, saved_dataframe, dataframe_json_data, dataframe_json_edited_data):

    helper = pdf = PortallDataFrameHelper(client)

    if mocked is True:
        mocker.patch.object(client, "post", return_value=saved_dataframe)
        mocker.patch.object(client, "put", return_value=saved_dataframe)

    dataframe = pd.DataFrame(dataframe_json_data)
    metadata = '{"company":23, "component":"23423-f334r-34r34-34r34"}'

    portall_df = PortallDataFrame.from_df(
        dataframe, 
        client=client, 
        name="New dataframe",
        metadata=metadata,
    )

    result = portall_df.save()

    edited_data = pd.DataFrame(dataframe_json_edited_data)

    edited_portall_df = PortallDataFrame.from_df(
        edited_data,
        id=portall_df.id,
        client=client, 
        name="Edited dataframe",
        metadata=metadata,
    )

    result = edited_portall_df.save()

    assert UUID(result['id'])

def test_dataframe_delete(mocker, mocked, client, saved_dataframe, dataframe_json_data):
    '''
    First we create a new dataframe and save it
    Then we delete it
    We assert the id is None
    '''

    helper = PortallDataFrameHelper(client)

    if mocked is True:
        mocker.patch.object(client, "delete", return_value=None)
        mocker.patch.object(client, "post", return_value=saved_dataframe)


    dataframe = pd.DataFrame(dataframe_json_data)
    metadata = '{"company":23, "component":"23423-f334r-34r34-34r34"}'

    portall_df = PortallDataFrame.from_df(
        dataframe, 
        client=client, 
        name="New dataframe",
        metadata=metadata,
    )

    result = portall_df.save()
    portall_df.delete()

    assert portall_df.id == None