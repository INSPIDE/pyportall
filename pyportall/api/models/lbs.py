from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field


class GeocodingOptions(BaseModel):
    """ Options to be used as fallback when the specific addresses do not have their own. """

    country: Optional[str] = Field("Spain", example="Spain", description="Country in English.")
    state: Optional[str] = Field(None, example="Comunidad de Madrid", description="State or region.")
    county: Optional[str] = Field(None, example="Madrid", description="County or province.")
    city: Optional[str] = Field(None, example="Madrid", description="City or municipality.")
    district: Optional[str] = Field(None, example="Justicia", description="District or neighborhood.")
    postal_code: Optional[str] = Field(None, example="28013", description="Postal code.")

    class Config:
        title = "Geocoding options"
        schema_extra = {
            "example": {
                "country": "Spain",
                "city": "Madrid"
            }
        }
