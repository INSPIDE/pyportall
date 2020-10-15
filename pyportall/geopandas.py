import pandas as pd
import geopandas as gpd
from typing import Any, Dict, List, Union
from shapely.geometry import Point, Polygon as ShapelyPolygon, shape

from .utils import jsonable_encoder
from .models import Indicator, Moment, Options, Position, Isoline, Isovist, Polygon
from .engine import GeocodingHelper as GeocodingHelperOrig, IsovistHelper as IsovistHelperOrig, IsolineHelper as IsolineHelperOrig, IndicatorHelper as IndicatorHelperOrig
from .geojson import Polygon as GeometryPolygon
from .exceptions import PyPortallException


def to_df(items: Union[List[Moment], List[Indicator], List[Options]]) -> pd.DataFrame:
    return pd.DataFrame(jsonable_encoder(items))


def to_gdf(locations: Union[List[Position], List[Isoline], List[Isovist], List[Polygon]]) -> gpd.GeoDataFrame:
    locations_raw = jsonable_encoder(locations)

    for location in locations_raw:
        if "geom" in location:
            location["geometry"] = ShapelyPolygon(shape(location["geom"]))
            del location["geom"]
        else:
            location["geometry"] = Point(location["lon"], location["lat"])
            del location["lon"]
            del location["lat"]

    return gpd.GeoDataFrame(locations_raw, crs="EPSG:4326")


def combine(left: gpd.GeoDataFrame, right: Union[pd.DataFrame, pd.Series]) -> gpd.GeoDataFrame:
    left["tmp"] = 1
    right["tmp"] = 1

    combination = pd.merge(left, right, on="tmp", how="outer")

    left.drop(columns=["tmp"])
    right.drop(columns=["tmp"])
    combination.drop(columns=["tmp"])

    return gpd.GeoDataFrame(combination, crs="EPSG:4326")


class GeocodingHelper(GeocodingHelperOrig):
    def from_series(self, series: pd.Series) -> gpd.GeoSeries:
        positions = [Position(address=address) for address in series]

        self.resolve(positions=positions)

        geometries = []
        for position in positions:
            geometries.append(Point(position.lon, position.lat))

        return gpd.GeoSeries(geometries)


class IsovistHelper(IsovistHelperOrig):
    def from_gdf(self, gdf: gpd.GeoDataFrame, radius_m_column: str = "radius_m", num_rays_column: str = "num_rays", heading_deg_column: str = "heading_deg", fov_deg_column: str = "fov_deg") -> gpd.GeoDataFrame:
        isovists = []

        for index, row in gdf.iterrows():
            isovist_params: Dict[str, Any] = {"destination": Position(lon=row["geometry"].x, lat=row["geometry"].y)}
            if radius_m_column in row:
                isovist_params[radius_m_column] = row[radius_m_column]
            if num_rays_column in row:
                isovist_params[num_rays_column] = row[num_rays_column]
            if heading_deg_column in row:
                isovist_params[heading_deg_column] = row[heading_deg_column]
            if fov_deg_column in row:
                isovist_params[fov_deg_column] = row[fov_deg_column]
            isovists.append(Isovist(**isovist_params))

        self.resolve(isovists)

        return gpd.GeoDataFrame(gdf.assign(geometry=[isovist.geom for isovist in isovists]), crs="EPSG:4326")


class IsolineHelper(IsolineHelperOrig):
    def from_gdf(self, gdf: gpd.GeoDataFrame, mode_column: str = "mode", range_s_column: str = "range_s") -> gpd.GeoDataFrame:
        isolines = [Isoline(destination=Position(lon=row["geometry"].x, lat=row["geometry"].y), mode=row[mode_column], range_s=row[range_s_column]) for index, row in gdf.iterrows()]

        self.resolve(isolines)

        return gpd.GeoDataFrame(gdf.assign(geometry=[isoline.geom for isoline in isolines]), crs="EPSG:4326")


class IndicatorHelper(IndicatorHelperOrig):
    def from_gdf(self, gdf: gpd.GeoDataFrame, indicator_column: str = "indicator") -> gpd.GeoDataFrame:
        values: List = []

        for index, row in gdf.iterrows():
            try:
                indicator = Indicator(code=row[indicator_column])
            except KeyError:
                raise PyPortallException(f"Indicator column '{indicator_column}' is missing from GeoDataFrame")
            location = Polygon(geom=GeometryPolygon(**row["geometry"].__geo_interface__))
            moment = Moment(dow=row["dow"], month=row["month"], hour=row["hour"])
            try:
                values.append(self.resolve([indicator], [location], [moment])[0].value)
            except IndexError:
                values.append(None)

        return gpd.GeoDataFrame(gdf.assign(value=values), crs="EPSG:4326")
