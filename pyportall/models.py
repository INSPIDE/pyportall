from enum import Enum
from pydantic import BaseModel, validator, root_validator
from pydantic.fields import Field
from pydantic.types import conint
from typing import Any, Optional
from datetime import datetime

from .geojson import Geometry, Polygon as GeometryPolygon


class Normalization(str, Enum):
    total = "total"
    density = "density"


Hour = conint(ge=0, le=23)


class DayOfWeek(str, Enum):
    sunday = "sunday"
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"


class Month(str, Enum):
    january = "january"
    february = "february"
    march = "march"
    april = "april"
    may = "may"
    june = "june"
    july = "july"
    august = "august"
    september = "september"
    october = "october"
    november = "november"
    december = "december"


class Options(BaseModel):
    country: Optional[str] = Field("Spain", example="Spain", description="Only useful if geocoding is needed to fulfill the request as part of the global geocoding context.")
    state: Optional[str] = Field(None, example="Comunidad de Madrid", description="State or region. Only useful if geocoding is needed to fulfill the request as part of the global geocoding context.")
    county: Optional[str] = Field(None, example="Madrid", description="County or province. Only useful if geocoding is needed to fulfill the request as part of the global geocoding context.")
    city: Optional[str] = Field(None, example="Madrid", description="City or municipality. Only useful if geocoding is needed to fulfill the request as part of the global geocoding context.")
    district: Optional[str] = Field(None, example="Justicia", description="District or neighborhood. Only useful if geocoding is needed to fulfill the request as part of the global geocoding context.")
    postal_code: Optional[str] = Field(None, example="28013", description="Only useful if geocoding is needed to fulfill the request as part of the global geocoding context.")

    class Config:
        schema_extra = {
            "example": {
                "country": "Spain",
                "city": "Madrid"
            }
        }

    @property
    def qq(self):
        return ";".join([f"{k if k != 'postal_code' else 'postalCode'}={v}" for k, v in self.__dict__.items() if v and k != "normalization"])


class Moment(BaseModel):
    id: Optional[str] = Field(None, example="7", description="Id that will be used in the response to refer to this moment.")
    dow: DayOfWeek = Field(..., example=DayOfWeek("friday"), description="Day of the week.")
    month: Month = Field(..., example=Month("february"))
    hour: Hour = Field(..., example=Hour(12))
    year: int = Field(2020, example=2020)

    class Config:
        schema_extra = {
            "example": {
                "id": "7",
                "dow": DayOfWeek("friday"),
                "month": Month("february"),
                "hour": Hour(12)
            }
        }

    @validator("dow", "month", pre=True)
    def lower(cls, v):
        return v.lower()

    @property
    def month_number(self) -> int:
        return ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"].index(self.month) + 1

    @property
    def dow_number(self) -> int:
        return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(self.dow) + 1  # TODO: isoweekdays

    @property
    def equivalent_datetime(self) -> datetime:
        for day_number in range(1, 8):
            equivalent_datetime = datetime(self.year, self.month_number, day_number, self.hour, 00)
            if equivalent_datetime.weekday() == self.dow_number - 1:
                return equivalent_datetime

        raise ValueError("Couldn't find equivalent date")


class Position(BaseModel):
    lon: Optional[float] = Field(None, example=-3.70012)
    lat: Optional[float] = Field(None, example=40.41998)
    address: Optional[str] = Field(None, example="Calle Gran Vía, 20, 28013 Madrid", description="Full or partial address. Can be translated into latitude/longitude by means of geocoding.")

    class Config:
        schema_extra = {
            "example": {
                "lon": -3.70012,
                "lat": 40.41998
            }
        }

    @root_validator(pre=True)
    def check_latlon_or_address(cls, values):
        assert ("lon" in values and "lat" in values) or "address" in values, "Either lon/lat or an address must be provided"

        return values

    @validator('lon')
    def validate_lon(cls, v):
        if v is not None:
            assert v > -180 and v < 180, "Longitude must be between -180 and 180"

        return v

    @validator('lat')
    def validate_lat(cls, v):
        if v is not None:
            assert v > -90 and v < 90, "Latitude must be between -90 and 90"

        return v


class IsolineMode(str, Enum):
    car = "car"
    truck = "truck"
    pedestrian = "pedestrian"


class Isoline(BaseModel):
    id: Optional[str] = Field(None, example="12", description="Id that will be used in the response to refer to this isoline.")
    destination: Position = Field(..., example=Position(address="Calle Gran Vía, 20, 28013 Madrid"), description="Focal point of the isoline.")
    mode: IsolineMode = Field(..., example=IsolineMode("car"), description="Means of transport used to calculate the isoline border.")
    range_s: conint(gt=0, le=3600) = Field(..., example=1000, description="Number of seconds to be taken into account to calculate the isoline border.")
    moment: Optional[Moment] = Field(None, example=Moment(dow="friday", month="february", hour=20), description="Moment in time to use when estimating the isoline border.")
    geom: Optional[Geometry] = Field(None, example=GeometryPolygon(coordinates=[[[-3.609563, 40.429004], [-3.611067, 40.422879], [-3.601402, 40.425862], [-3.609563, 40.429004]]]), description="Isoline border geometry once calculated.")

    class Config:
        schema_extra = {
            "example": {
                "id": "12",
                "destination": Position(address="Calle Gran Vía, 20, 28013 Madrid"),
                "mode": IsolineMode("car"),
                "range_s": 1000
            }
        }


class Isovist(BaseModel):
    id: Optional[str] = Field(None, example="12", description="Id that will be used in the response to refer to this isovist.")
    destination: Position = Field(..., example=Position(address="Calle Gran Vía, 20, 28013 Madrid"), description="Focal point of the isovist.")
    radius_m: int = Field(150, example=150, description="Maximum number of meters to be taken into account to calculate the isovist border.")
    num_rays: int = Field(-1, example=-1, description="Number of angular steps that will define the resolution (-1 means 1 ray per field of view degree).")
    heading_deg: int = Field(0, example=0, description="Northing in degrees, to set the direction the eyeballs are looking at.")
    fov_deg: int = Field(360, example=360, description="Field of view in degrees, centered in the heading direction.")
    geom: Optional[Geometry] = Field(None, example=GeometryPolygon(coordinates=[[[-3.609563, 40.429004], [-3.611067, 40.422879], [-3.601402, 40.425862], [-3.609563, 40.429004]]]), description="Isovist border geometry once calculated.")

    class Config:
        schema_extra = {
            "example": {
                "id": "12",
                "destination": Position(address="Calle Gran Vía, 20, 28013 Madrid"),
                "radius_m": 1000
            }
        }


class Polygon(BaseModel):
    id: Optional[str] = Field(None, example="12", description="Id that will be used in the response to refer to this polygon.")
    geom: Geometry = Field(..., example=GeometryPolygon(coordinates=[[[-3.609563, 40.429004], [-3.611067, 40.422879], [-3.601402, 40.425862], [-3.609563, 40.429004]]]), description="Polygon geometry.")

    class Config:
        schema_extra = {
            "example": {
                "id": "12",
                "geom": GeometryPolygon(coordinates=[[[-3.609563, 40.429004], [-3.611067, 40.422879], [-3.601402, 40.425862], [-3.609563, 40.429004]]])
            }
        }


class Indicator(BaseModel):
    code: str = Field(..., example="pop", description="Indicator code as defined in the metadata database.")
    normalization: Optional[Normalization] = Field(Normalization("total"), example=Normalization("total"), description="Geospatial normalization. Only useful when requesting indicators.")
    location: Optional[str] = Field(None, example="12", description="Id that refers to the corresponding location in a request.")
    moment: Optional[str] = Field(None, example="7", description="Id that refers to the corresponding moment in a request.")
    value: Optional[Any] = Field(None, example="443", description="Actual value of the indicator for the given location and moment.")

    class Config:
        schema_extra = {
            "example": {
                "code": "pop",
                "normalization": Normalization("total"),
                "location": "12",
                "moment": "7",
                "value": 443
            }
        }


class JobStatus(BaseModel):
    detail: str = Field(..., example="Pending", description="Present when the job is still being processed.")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Pending"
            }
        }
