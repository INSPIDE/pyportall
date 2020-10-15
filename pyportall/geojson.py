# Blatantly stolen from https://github.com/developmentseed/geojson-pydantic
# We should use geojson-pydantic as soon as it matures as a project
import abc
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from typing import Tuple, Union
from typing import Any, Dict, List, Optional, Tuple, Union


NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    coordinates: Any  # will be constrained in child classes

    @property
    def __geo_interface__(self):
        return self.dict()


Coordinate = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]

Position = Coordinate


class Point(_GeometryBase):
    """Point Model"""

    type: str = Field("Point", const=True)
    coordinates: Coordinate


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: str = Field("MultiPoint", const=True)
    coordinates: List[Coordinate]


class LineString(_GeometryBase):
    """LineString Model"""

    type: str = Field("LineString", const=True)
    coordinates: List[Coordinate] = Field(..., min_items=2)


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: str = Field("MultiLineString", const=True)
    coordinates: List[List[Coordinate]]


class Polygon(_GeometryBase):
    """Polygon Model"""

    type: str = Field("Polygon", const=True)
    coordinates: List[List[Coordinate]]

    @validator("coordinates")
    def check_coordinates(cls, coords):
        """Validate that Polygon coordinates pass the GeoJSON spec"""
        if any([len(c) < 4 for c in coords]):
            raise ValueError("All linear rings must have four or more coordinates")
        if any([c[-1] != c[0] for c in coords]):
            raise ValueError("All linear rings have the same start and end coordinates")
        return coords


class MultiPolygon(_GeometryBase):
    """MultiPolygon Model"""

    type: str = Field("MultiPolygon", const=True)
    coordinates: List[List[List[Coordinate]]]


Geometry = Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]


class GeometryCollection(BaseModel):
    """GeometryCollection Model"""

    type: str = Field("GeometryCollection", const=True)
    geometries: List[Geometry]

    def __iter__(self):
        """iterate over geometries"""
        return iter(self.geometries)

    def __len__(self):
        """return geometries length"""
        return len(self.geometries)

    def __getitem__(self, index):
        """get geometry at a given index"""
        return self.geometries[index]


def parse_geometry_obj(obj) -> Geometry:
    """
    `obj` is an object that is supposed to represent a GeoJSON geometry. This method returns the
    reads the `"type"` field and returns the correct pydantic Geometry model.
    """
    if "type" not in obj:
        raise ValidationError(
            [
                ErrorWrapper(ValueError("Missing 'type' field in geometry"), "type"),
                "Geometry",
            ]
        )
    if obj["type"] == "Point":
        return Point.parse_obj(obj)
    elif obj["type"] == "MultiPoint":
        return MultiPoint.parse_obj(obj)
    elif obj["type"] == "LineString":
        return LineString.parse_obj(obj)
    elif obj["type"] == "MultiLineString":
        return MultiLineString.parse_obj(obj)
    elif obj["type"] == "Polygon":
        return Polygon.parse_obj(obj)
    elif obj["type"] == "MultiPolygon":
        return MultiPolygon.parse_obj(obj)
    raise ValidationError(
        [ErrorWrapper(ValueError("Unknown type"), "type")], "Geometry"
    )



class Feature(BaseModel):
    """Feature Model"""

    type: str = Field("Feature", const=True)
    geometry: Geometry
    properties: Optional[Dict[Any, Any]]
    id: Optional[str]
    bbox: Optional[BBox]

    class Config:
        """TODO: document"""

        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v):
        """set geometry from geo interface or input"""
        if hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        return v


class FeatureCollection(BaseModel):
    """FeatureCollection Model"""

    type: str = Field("FeatureCollection", const=True)
    features: List[Feature]
    bbox: Optional[BBox]

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]
