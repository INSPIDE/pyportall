import logging
from typing import Dict, List, Union


from pyportall.api.engine.core import APIClient, APIHelper
from pyportall.api.models.metadata import IndicatorMetadata


logger = logging.getLogger("metadata")


class MetadataHelper(APIHelper):
    def __init__(self, client: APIClient) -> None:
        super().__init__(client)

        self.metadata: Dict[str, IndicatorMetadata] = {indicator["code"]: IndicatorMetadata(**indicator) for indicator in self.client.call_metadata()}

    def all(self) -> List[IndicatorMetadata]:
        return [indicator for indicator in self.metadata.values()]

    def get(self, indicator_code: str) -> Union[IndicatorMetadata, None]:
        return self.metadata.get(indicator_code)

    def refresh(self) -> None:
        self.metadata = {indicator["code"]: IndicatorMetadata(**indicator) for indicator in self.client.call_metadata()}
