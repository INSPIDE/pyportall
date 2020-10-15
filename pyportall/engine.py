from typing import Any, Dict, List, Optional, Union

from .models import Indicator, Isoline, Isovist, Moment, Options, Polygon, Position
from .utils import jsonable_encoder
from .api import APIClient, ENDPOINT_POLYGONS, ENDPOINT_GEOCODING, ENDPOINT_RESOLVE_ISOLINES, ENDPOINT_RESOLVE_ISOVISTS
from .geojson import Polygon as GeometryPolygon


class APIHelper:
    def __init__(self, client: APIClient) -> None:
        self.client = client


class GeocodingHelper(APIHelper):
    def __init__(self, client: APIClient, options: Optional[Options] = None) -> None:
        self.options = options
        super().__init__(client)

    def from_addresses(self, addresses: List[str]) -> List[Position]:
        positions = [Position(address=address) for address in addresses]

        self.resolve(positions=positions)

        return positions

    def resolve(self, positions: List[Position]) -> None:
        api_input: Dict[str, Any] = {"locations": [position.dict() for position in positions]}

        if self.options is not None:
            api_input["options"] = self.options.dict()

        raw_geocoded_positions = self.client.call(ENDPOINT_GEOCODING, api_input)

        for (original_position, raw_geocoded_position) in zip (positions, raw_geocoded_positions):
            original_position.lon = raw_geocoded_position["lon"]
            original_position.lat = raw_geocoded_position["lat"]

        return None


class IsovistHelper(APIHelper):
    def resolve(self, isovists: List[Isovist]) -> None:
        api_input: Dict[str, Any] = {"locations": [isovist.dict() for isovist in isovists]}

        resolved_isovists = self.client.call(ENDPOINT_RESOLVE_ISOVISTS, api_input)

        for (original_isovist, resolved_isovist) in zip (isovists, resolved_isovists):
            original_isovist.geom = GeometryPolygon(**resolved_isovist["geom"])

        return None


class IsolineHelper(APIHelper):
    def resolve(self, isolines: List[Isoline]) -> None:
        api_input: Dict[str, Any] = {"locations": [isoline.dict() for isoline in isolines]}

        resolved_isolines = self.client.call(ENDPOINT_RESOLVE_ISOLINES, api_input)

        for (original_isoline, resolved_isoline) in zip (isolines, resolved_isolines):
            original_isoline.geom = GeometryPolygon(**resolved_isoline["geom"])

        return None


class IndicatorHelper(APIHelper):
    def __init__(self, client: APIClient, options: Optional[Options] = None) -> None:
        self.options = options
        super().__init__(client)

    def resolve(self, indicators: List[Indicator], locations: List[Union[Polygon, Isoline, Isovist]], moments: List[Moment]) -> List[Indicator]:
        for i, location in enumerate(locations):
            if location.id is None:
                location.id = str(i)

        for i, moment in enumerate(moments):
            if moment.id is None:
                moment.id = str(i)

        api_input: Dict[str, Any] = jsonable_encoder({
            "indicators": indicators,
            "locations": locations,
            "moments": moments
        })

        if self.options is not None:
            api_input["options"] = self.options.dict()

        raw_indicators = self.client.call(ENDPOINT_POLYGONS, api_input)

        return [Indicator(**indicator) for indicator in raw_indicators]
