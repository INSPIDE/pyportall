import json
import pandas as pd
import geopandas as gpd
from typing import Optional
from shapely.geometry import Polygon, mapping

from pyportall.utils import jsonable_encoder
from pyportall.api.engine.core import APIHelper, ENDPOINT_AGGREGATED_INDICATORS, ENDPOINT_DISAGGREGATED_INDICATORS, ENDPOINT_GEOCODING, ENDPOINT_RESOLVE_ISOLINES, ENDPOINT_RESOLVE_ISOVISTS
from pyportall.api.models.lbs import GeocodingOptions
from pyportall.api.models.indicators import Indicator, Moment


class GeocodingHelper(APIHelper):
    def resolve(self, df: pd.DataFrame, options: Optional[GeocodingOptions] = None) -> gpd.GeoDataFrame:
        features = self.client.call_indicators(ENDPOINT_GEOCODING, {"df": df.to_dict(), "options": jsonable_encoder(options)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class IsovistHelper(APIHelper):
    def resolve(self, gdf: gpd.GeoDataFrame, options: Optional[GeocodingOptions] = None) -> gpd.GeoDataFrame:
        features = self.client.call_indicators(ENDPOINT_RESOLVE_ISOVISTS, {"gdf": json.loads(gdf.to_json()), "options": jsonable_encoder(options)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class IsolineHelper(APIHelper):
    def resolve(self, gdf: gpd.GeoDataFrame, options: Optional[GeocodingOptions] = None) -> gpd.GeoDataFrame:
        features = self.client.call_indicators(ENDPOINT_RESOLVE_ISOLINES, {"gdf": json.loads(gdf.to_json()), "options": jsonable_encoder(options)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class IndicatorHelper(APIHelper):
    def resolve_aggregated(self, gdf: gpd.GeoDataFrame, indicator: Optional[Indicator] = None, moment: Optional[Moment] = None) -> gpd.GeoDataFrame:
        features = self.client.call_indicators(ENDPOINT_AGGREGATED_INDICATORS, {"gdf": json.loads(gdf.to_json()), "indicator": jsonable_encoder(indicator), "moment": jsonable_encoder(moment)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")

    def resolve_disaggregated(self, polygon: Polygon, indicator: Indicator, moment: Moment) -> gpd.GeoDataFrame:
        features = self.client.call_indicators(ENDPOINT_DISAGGREGATED_INDICATORS, {"polygon": mapping(polygon), "indicator": jsonable_encoder(indicator), "moment": jsonable_encoder(moment)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")
