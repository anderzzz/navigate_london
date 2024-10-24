"""Select APIs for the TFL API.

"""
from typing import Sequence, Optional
from enum import Enum

from client import TFLClient

class Modes(Enum):
    BUS = 'bus'
    TUBE = 'tube'
    RAIL = 'rail'
    TRAM = 'tram'
    RIVER_BUS = 'river-bus'


class SearchStopPoints:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'StopPoint/Search'

    def __call__(self,
                 query: str,
                 modes: Optional[Sequence[Modes]] = None,
                 ):
        """Search for stop points, such as bus stops, tube stations, by their common name.

        Args:
            query: The search query, a case-insensitive string that will be matched against the common name of the stop points.


        """
        params = {'query': query}
        if modes:
            params['modes'] = ','.join(mode.value for mode in modes)

        return self.client.get(self._endpoint, params=params)
