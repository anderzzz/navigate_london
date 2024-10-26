"""Select APIs for the TFL API.

"""
from typing import Sequence, Optional, Dict, Union, Tuple
from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime

from tfl_api import TFLClient
from utils import slice_dict

#
# Define the parameters for the journey planner
#
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


#
# Define and execute the API call for journey planner
#
class JourneyPlannerSearch:
    def __init__(self, client: TFLClient):
        self.client = client
        self._endpoint = 'Journey/JourneyResults'
        self.status_code = None

    def __call__(self,
                 from_loc: str,
                 to_loc: str,
                 **params):
        """Plan a journey between two locations, given a set of preferences and times.
        
        """
        _url = f'{self._endpoint}/{from_loc}/to/{to_loc}'
        self.status_code, payload = self.client.get(_url, params=params)
        return payload


#
# Define the payload post-processing
#
def _disambiguate_loc(option, match_thrs) -> Optional[Union[str, Tuple[float, float]]]:
    if float(option['matchQuality']) < match_thrs:
        return None

    if 'icsCode' in option['place']:
        return option['place']['icsCode']
    elif 'lat' in option['place'] and 'lon' in option['place']:
        return option['place']['lat'], option['place']['lon']
    elif 'naptanId' in option['place']:
        return option['place']['naptanId']
    else:
        raise RuntimeError(f'Could not disambiguate location in payload: {option}')


class JourneyPlannerSearchPayloadProcessor:
    """Process the payload from the journey planner.

    """
    def __init__(self,
                 matching_threshold: float = 900.0,
                 ):
        self.matching_threshold = matching_threshold

        self.MATCH_STATUS_TO_DISAMBIGUATE = ['list']
        self.MATCH_STATUS_MATCHED = ['identified']
        self.MATCH_STATUS_EMPTY = ['empty']

        self._loc_from = None
        self._loc_to = None
        self._loc_via = None

    def journeys(self,
                 payload: Dict,
                 leg_data_to_retrieve: Optional[Sequence[Sequence[str]]] = None
                 ):
        """Process the payload from the journey planner.

        """
        for journey in payload['journeys']:
            ret = {
                'start_date_time': journey['startDateTime'],
                'end_date_time': journey['endDateTime'],
                'duration': journey['duration'],
            }
            leg_ = {}
            for leg in journey['legs']:
                if leg_data_to_retrieve is not None:
                    leg_data = slice_dict(leg, leg_data_to_retrieve)
                    leg_.update(leg_data)
            ret['legs'] = leg_

            yield ret

    def journey_vectors(self, payload: Dict):
        """Retrieve the journey vectors from the payload.

        """
        pass

    def _disambiguate_loc_type(self, type_: str, payload: Dict):
        ret = []
        if f'{type_}LocationDisambiguation' in payload:
            if payload[f'{type_}LocationDisambiguation']['matchStatus'] in self.MATCH_STATUS_TO_DISAMBIGUATE:
                ret = [_disambiguate_loc(option, self.matching_threshold) for option in payload[f'{type_}LocationDisambiguation']['disambiguationOptions']]
            elif payload[f'{type_}LocationDisambiguation']['matchStatus'] in self.MATCH_STATUS_MATCHED:
                ret = [True]
            elif payload[f'{type_}LocationDisambiguation']['matchStatus'] in self.MATCH_STATUS_EMPTY:
                ret = [False]
            else:
                raise RuntimeError(f'Unknown match status: {payload[f"{type_}LocationDisambiguation"]["matchStatus"]}')

        return [x for x in ret if x is not None]

    def disambiguate(self, payload: Dict):
        """Disambiguate the payload from the journey planner.

        """
        self._loc_from = self._disambiguate_loc_type('from', payload)
        self._loc_to = self._disambiguate_loc_type('to', payload)
        self._loc_via = self._disambiguate_loc_type('via', payload)

    def transform_loc(self, type_: str, loc):
        try:
            val = getattr(self, f'_loc_{type_}')
        except AttributeError:
            raise ValueError(f'Unknown location type: {type_}')

        if val[0] is True:
            return [loc]
        elif val[0] is False:
            return [None]
        else:
            return val
