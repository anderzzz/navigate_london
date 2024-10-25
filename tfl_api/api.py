"""Select APIs for the TFL API.

"""
from typing import Sequence, Optional
from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime

from tfl_api import TFLClient

class Mode(str, Enum):
    """The modes of transportation."""
    BUS = "public-bus"
    TUBE = "tube"
    TRAIN = "train"
    OVERGROUND = "overground"
    RIVER = "river"
    TRAM = "tram"
    WALKING = "walking"
    CYCLE = "cycle"
    COACH = "coach"


class AccessibilityPreference(str, Enum):
    """Preferences for accessibility."""
    NO_SOLID_STAIRS = "noSolidStairs"
    NO_ESCALATORS = "noEscalators"
    NO_ELEVATORS = "noElevators"
    STEP_FREE_TO_VEHICLE = "stepFreeToVehicle"
    STEP_FREE_TO_PLATFORM = "stepFreeToPlatform"


class WalkingSpeed(str, Enum):
    """Speeds of walking."""
    SLOW = "slow"
    AVERAGE = "average"
    FAST = "fast"


class JourneyPreference(str, Enum):
    """Preferences on what to optimize in journey planning."""
    LEAST_INTERCHANGE = "leastinterchange"
    LEAST_WALKING = "leastwalking"
    LEAST_TIME = "leasttime"


class CyclePreference(str, Enum):
    """Preferences on cycling."""
    ALL_THE_WAY = "allTheWay"
    LEAVE_AT_STATION = "leaveAtStation"
    TAKE_ON_TRANSPORT = "takeOnTransport"
    CYCLE_HIRE = "cycleHire"


class Adjustment(str, Enum):
    """Adjustments to the journey."""
    TRIP_FIRST = "TripFirst"
    TRIP_LAST = "TripLast"


class BikeProficiency(str, Enum):
    """Proficiency in cycling."""
    EASY = "easy"
    MODERATE = "moderate"
    FAST = "fast"


class TimeIs(str, Enum):
    """Specification on what a time of day denotes."""
    DEPARTING = "departing"
    ARRIVING = "arriving"


class JourneyModesAvailable:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'Journey/Meta/Modes'

    def __call__(self):
        """Retrieve all available transportation modes that the journey planner API deals with.

        """
        return self.client.get(self._endpoint)


class JourneyPlannerSearchParams(BaseModel):
    via: Optional[str] = None
    national_search: Optional[bool] = None
    date: Optional[str] = None
    time: Optional[str] = None
    time_is: Optional[TimeIs] = None
    journey_preference: Optional[JourneyPreference] = None
    mode: Optional[Sequence[Mode]] = None
    accessibility_preference: Optional[Sequence[AccessibilityPreference]] = None
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    via_name: Optional[str] = None
    max_transfer_minutes: Optional[int] = None
    max_walking_minutes: Optional[int] = None
    walking_speed: Optional[WalkingSpeed] = None
    cycle_preference: Optional[CyclePreference] = None
    adjustment: Optional[Adjustment] = None
    bike_proficiency: Optional[Sequence[BikeProficiency]] = None
    alternative_cycle: Optional[bool] = None
    alternative_walking: Optional[bool] = None
    walking_optimization: Optional[bool] = None
    taxi_only_trip: Optional[bool] = None

    @field_validator('date')
    @classmethod
    def validate_date(cls, d):
        try:
            datetime.strptime(d, '%Y%m%d')
        except ValueError:
            raise ValueError('Date must be in format YYYYMMDD')
        return d

    @field_validator('time')
    @classmethod
    def validate_time(cls, t):
        try:
            datetime.strptime(t, '%H%M')
        except ValueError:
            raise ValueError('Time must be in format HHMM')
        return t

    @field_validator('mode',
                     'time_is',
                     'journey_preference',
                     'accessibility_preference',
                     'walking_speed',
                     'cycle_preference',
                     'adjustment',
                     'bike_proficiency')
    @classmethod
    def validate_enum(cls, v):
        if v is not None and type(v) is str:
            enum_type = cls.__model_fields__[v].type_
            if isinstance(v, str):
                try:
                    return enum_type(v)
                except ValueError:
                    raise ValueError(f'{v} is not a valid value for this field')
            elif isinstance(v, Sequence):
                try:
                    return [enum_type(item) for item in v]
                except ValueError:
                    raise ValueError(f'One or more values in {v} are not valid for this field')
        return v


class JourneyPlannerSearch:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'Journey/JourneyResults'

    def __call__(self,
                 from_loc: str,
                 to_loc: str,
                 **params):
        """Plan a journey between two locations, given a set of preferences and times.
        
        """
        _url = f'{self._endpoint}/{from_loc}/to/{to_loc}'
        return self.client.get(_url, params=params)


class SearchStopPoints:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'StopPoint/Search'

    def __call__(self,
                 query: str,
                 modes: Optional[Sequence[Mode]] = None,
                 ):
        """Search for stop points, such as bus stops, tube stations, by their common name.

        Args:
            query: The search query, a case-insensitive string that will be matched against the common name of the stop points.


        """
        params = {'query': query}
        if modes:
            params['modes'] = ','.join(mode.value for mode in modes)

        return self.client.get(self._endpoint, params=params)
