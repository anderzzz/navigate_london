"""Select APIs for the TFL API.

"""
from typing import Sequence, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator

from tfl_api import TFLClient

class Modes(Enum):
    BUS = 'bus'
    TUBE = 'tube'
    RAIL = 'rail'
    TRAM = 'tram'
    RIVER_BUS = 'river-bus'


class WalkingSpeed(str, Enum):
    SLOW = "slow"
    AVERAGE = "average"
    FAST = "fast"


class JourneyPreference(str, Enum):
    LEAST_INTERCHANGE = "least_interchange"
    LEAST_WALKING = "least_walking"
    LEAST_TIME = "least_time"


class TimeIs(str, Enum):
    DEPARTING = "departing"
    ARRIVING = "arriving"


class JourneyModesAvailable:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'Journey/Meta/Modes'

    def __call__(self):
        """Retrieve all available transportation modes that the journey planner API deals with

        """
        return self.client.get(self._endpoint)


class JourneyPlannerSearchParams(BaseModel):
    via: Optional[str] = None
    national_search: Optional[bool] = None
    date: Optional[str] = None
    time: Optional[str] = None
    time_is: Optional[str] = None
    journey_preference: Optional[str] = None
    mode: Optional[str] = None
    accessibility_preference: Optional[str] = None
    max_transfer_minutes: Optional[int] = None
    max_walking_minutes: Optional[int] = None
    walking_speed: Optional[str] = None
    cycle_preference: Optional[str] = None
    adjustment: Optional[str] = None
    bike_proficiency: Optional[str] = None
    alternative_cycle: Optional[bool] = None
    alternative_walking: Optional[bool] = None
    walking_optimization: Optional[bool] = None
    taxi_only: Optional[bool] = None


class JourneyPlannerSearch:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'Journey/JourneyResults'

    def __call__(self,
                 from_loc: str,
                 to_loc: str,
                 **params):
        """
                 via: Optional[str] = None,
                 national_search: Optional[bool] = None,
                 date: Optional[str] = None,
                 time: Optional[str] = None,
                 time_is: Optional[str] = None,
                 journey_preference: Optional[str] = None,
                 mode: Optional[str] = None,
                 accessibility_preference: Optional[str] = None,
                 max_transfer_minutes: Optional[int] = None,
                 max_walking_minutes: Optional[int] = None,
                 walking_speed: Optional[str] = None,
                 cycle_preference: Optional[str] = None,
                 adjustment: Optional[str] = None,
                 bike_proficiency: Optional[str] = None,
                 alternative_cycle: Optional[bool] = None,
                 alternative_walking: Optional[bool] = None,
                 walking_optimization: Optional[bool] = None,
                 taxi_only: Optional[bool] = None,"""
        """Plan a journey between two locations.
        
        """
        _url = f'{self._endpoint}/{from_loc}/to/{to_loc}'
        return self.client.get(_url, params=params)


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
