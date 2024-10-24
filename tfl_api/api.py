"""Select APIs for the TFL API.

"""
from typing import Sequence, Optional
from enum import Enum

from tfl_api import TFLClient

class Modes(Enum):
    BUS = 'bus'
    TUBE = 'tube'
    RAIL = 'rail'
    TRAM = 'tram'
    RIVER_BUS = 'river-bus'


class JourneyModesAvailable:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'Journey/Meta/Modes'

    def __call__(self):
        """Retrieve all available transportation modes that the journey planner API deals with

        """
        return self.client.get(self._endpoint)


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
