"""Portall's GeoDataFrame wrappers."""
from __future__ import annotations

import geopandas as gpd
import pandas as pd
from typing import Optional
from pydantic.types import UUID4
from pydantic import BaseModel, Field, Json
from enum import Enum

from pyportall.api.engine.core import APIClient, ENDPOINT_DATAFRAMES
from pyportall.api.models.geojson import FeatureCollection, Feature, Polygon
from pyportall.exceptions import ValidationError


class PortallDataFrame(pd.DataFrame):
    """ GeoDataFrame with Portall superpowers. """

    def __init__(self, client: APIClient, name: Optional[str] = None, id: Optional[UUID4] = None, description: Optional[str] = None, metadata: Optional[Json] = None, *args, **kwargs) -> None:
        """Class constructor to attach the corresponding API client.

        Args:
            client: API client object to be used to send requests to the dataframe API.
            name: Dataframe name in Portall.
            id: Dataframe ID in Portall.
            description: Dataframe description in Portall.
        """
        super().__init__(*args, **kwargs)  # Needs to go first, otherwise you get a RecursionError from Pandas

        self.client = client
        self.name = name
        self.id = id
        self.description = description
        self.metadata = metadata

    @staticmethod
    def from_df(df: pd.DataFrame, client: APIClient, name: Optional[str] = None, id: Optional[UUID4] = None, description: Optional[str] = None, metadata: Optional[Json] = None) -> PortallDataFrame:
        """Build from Pandas DataFrame.

        Return a PortallDataFrame object out of a standard GeoPandas' GeoDataFrame.

        Args:
            gdf: GeoDataFrame to build the new PortallDataFrame object from.
            client: API client object to be used to send requests to the dataframe API.
            name: Dataframe name in Portall.
            id: Dataframe ID in Portall.
            description: Dataframe description in Portall.
            metadata: any other data goes here in json

        Returns:
            A new PortallDataFrame object.
        """
        pdf = PortallDataFrame(client, name=name, id=id, description=description, metadata=metadata)
        pdf.__dict__.update(df.__dict__)

        return pdf


    @staticmethod
    def from_api(pdf_api: PortallDataFrameAPI, client: APIClient) -> PortallDataFrame:
        """Build from a Portall dataframe as returned directly by Portall's API.

        Return a PortallDataFrame object out of a Portall dataframe as returned directly by Portall's API.

        Args:
            pdf_api: PortallDataFrameAPI object to build the new PortallDataFrame object from.
            client: API client object to be used to send requests to the dataframe API.

        Returns:
            A new PortallDataFrame object.
        """
        return PortallDataFrame.from_df(pdf_api.data, client, name=pdf_api.name, id=pdf_api.id, description=pdf_api.description)

    def save(self) -> None:
        """Persist dataframe in Portall.

        Creates or updates an equivalent, remote PortallDataFrame object in Portall.
        """
        try:
            pdf_api = PortallDataFrameAPI(
                id=getattr(self, "id", None), 
                name=getattr(self, "name"), 
                description=getattr(self, "descripton", None), 
                data_type=DataTypeEnum.json,
                data=self.to_json(),
                metadata=getattr(self, "metadata", None)
            )
        except AttributeError:
            raise ValidationError

        if pdf_api.id is None:
            return self.client.post(ENDPOINT_DATAFRAMES, body=pdf_api.json(exclude_none=True))
        else:
            return self.client.put(f"{ENDPOINT_DATAFRAMES}{pdf_api.id}/", body=pdf_api.json(exclude_none=True))

    def delete(self) -> None:
        """Delete dataframe in Portall.

        Deletes remote PortallDataFrame object in Portall. It will not delete the actual Python object.
        """
        try:
            pdf_api = PortallDataFrameAPI(id=getattr(self, "id", None), name=getattr(self, "name"), description=getattr(self, "descripton", ""), geojson=self.to_json())
        except AttributeError:
            raise ValidationError

        self.client.delete(f"{ENDPOINT_DATAFRAMES}{pdf_api.id}/")
        self.id = None

class DataTypeEnum(str, Enum):
    json = 'json'


class PortallDataFrameAPI(BaseModel):
    """ Representation of a Portall dataframe straight from the API. """

    id: Optional[UUID4] = Field(None, example="df30e466-1f68-42e5-8f4c-eceb1ebda89a", description="Portall ID of the saved dataframe in question.")
    name: str = Field(..., example="Population")
    description: Optional[str] = Field("", example="Population information in my trade areas.")
    data_type: DataTypeEnum = DataTypeEnum.json
    data: Json
    metadata: Json

