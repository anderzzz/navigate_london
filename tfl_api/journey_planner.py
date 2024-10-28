"""Select APIs for the TFL API.

"""
from typing import Sequence, Optional, Dict, Union, Tuple, Any, Generator, List
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime

from tfl_api import TFLClient
from utils import slice_dict

#
# Search parameters and functionality for the Journey Planner
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


def to_camel(s):
    return ''.join(word.capitalize() for word in s.split('_'))


class JourneyPlannerSearchParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    national_search: Optional[bool] = None
    date: Optional[str] = None
    time: Optional[str] = None
    time_is: Optional[TimeIs] = None
    journey_preference: Optional[JourneyPreference] = None
    mode: Optional[Sequence[Mode]] = None
    accessibility_preference: Optional[Sequence[AccessibilityPreference]] = None
    from_name: Optional[str] = None
    to_name: Optional[str] = None
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

    @field_validator('mode','time_is', 'journey_preference', 'accessibility_preference', 'walking_speed', 'cycle_preference', 'adjustment', 'bike_proficiency')
    @classmethod
    def validate_enum_list(cls, v):
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
        self.status_code = None

    def __call__(self,
                 from_loc: Union[str, Tuple[float, float]],
                 to_loc: Union[str, Tuple[float, float]],
                 params: JourneyPlannerSearchParams,
                 ):
        """Plan a journey between two locations, given a set of preferences and times.
        
        """
        from_loc = self._normalize_loc(from_loc)
        to_loc = self._normalize_loc(to_loc)
        _url = f'{self._endpoint}/{from_loc}/to/{to_loc}'
        self.status_code, payload = self.client.get(
            _url,
            params=params.model_dump(by_alias=True)
        )
        return payload

    @staticmethod
    def _normalize_loc(loc):
        if isinstance(loc, tuple):
            return f'{loc[0]},{loc[1]}'
        return loc


#
# Output payload processing parameter and functionality for the Journey Planner
#

@dataclass
class FieldMapping:
    target_field: str
    source_path: str
    description: str


JOURNEY_MAIN_DATA = [
    FieldMapping('start_date_time', 'startDateTime', 'The start date and time of the journey'),
    FieldMapping('end_date_time', 'arrivalDateTime', 'The end date and time of the journey'),
    FieldMapping('duration', 'duration', 'The duration of the journey in minutes'),
]
JOURNEY_LEG_DATA = [
    FieldMapping('start_date_time', 'departureTime', 'The start date and time of the leg'),
    FieldMapping('end_date_time', 'arrivalTime', 'The end date and time of the leg'),
    FieldMapping('duration', 'duration', 'The duration of the leg in minutes'),
    FieldMapping('instruction', 'instruction.detailed', 'The instruction for the leg'),
    FieldMapping('departure_point', 'departurePoint.commonName', 'The departure point of the leg'),
    FieldMapping('arrival_point', 'arrivalPoint.commonName', 'The arrival point of the leg'),
    FieldMapping('mode_transport', 'mode.name', 'The mode of transport for the leg'),
]



def _disambiguate_loc(option, match_thrs) -> Optional[Union[str, Tuple[float, float]]]:
    """Given that the TFL API returns a list of disambiguation options, select the data that allows
    another search to be performed. Stations are best identified by their ics codes, while locations
    generally by their lat/lon coordinates.

    """
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


def _get_nested_value(d: Dict, path: Sequence[str]) -> Any:
    """Helper function to get a value from a nested dictionary."""
    return _get_nested_value(d.get(path[0], {}), path[1:]) if path else d


class JourneyPlannerSearchPayloadProcessor:
    """Process the payload from the journey planner.

    """
    def __init__(self,
                 matching_threshold: float = 900.0,
                 leg_data_to_retrieve: Sequence[str] = ('mode of transport',),
                 ):
        self.matching_threshold = matching_threshold
        self.leg_data_to_retrieve = leg_data_to_retrieve
        for field in self.leg_data_to_retrieve:
            if not any(field in mapping.target_field for mapping in JOURNEY_LEG_DATA):
                raise ValueError(f'Unknown field to retrieve: {field}')

        self.MATCH_STATUS_TO_DISAMBIGUATE = ['list']
        self.MATCH_STATUS_MATCHED = ['identified']
        self.MATCH_STATUS_EMPTY = ['empty']

        self._loc_from = None
        self._loc_to = None
        self._payload_description = {}

    def journeys(self,
                 payload: Dict,
                 ) -> Generator[Dict[str, List[Dict]], None, None]:
        """Process a non-ambiguous payload from the journey planner.

        Select items from the nested and complex payload are extracted and yielded as a dictionary for
        each journey alternative.

        """
        for journey in payload['journeys']:
            j_data = {
                field.target_field: _get_nested_value(journey, field.source_path.split('.'))
                for field in JOURNEY_MAIN_DATA
            }
            self._payload_description.update(
                {field.target_field: field.description for field in JOURNEY_MAIN_DATA}
            )

            legs = []
            for leg in journey['legs']:
                leg_data = {}
                for leg_data_key in self.leg_data_to_retrieve:
                    try:
                        source_path = next(mapping.source_path for mapping in JOURNEY_LEG_DATA if mapping.target_field == leg_data_key)
                    except StopIteration:
                        raise ValueError(f'Unknown field to retrieve: {leg_data_key}')

                    leg_data_value = _get_nested_value(leg, source_path.split('.'))
                    leg_data[leg_data_key] = leg_data_value

                    self._payload_description.update(
                        {leg_data_key: next(mapping.description for mapping in JOURNEY_LEG_DATA if mapping.target_field == leg_data_key)}
                    )
                legs.append(leg_data)
            j_data['legs'] = legs

            yield j_data

    @property
    def payload_description(self):
        return self._payload_description

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
