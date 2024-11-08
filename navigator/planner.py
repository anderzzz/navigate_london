"""Bla bla

"""
from typing import Sequence, Dict, Optional, Union, List
from dataclasses import dataclass, asdict
import itertools
import json

from tfl_api import (
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
    get_description_for_field_
)


def _filter_none(value):
    if isinstance(value, list):
        return [_filter_none(v) for v in value]
    elif isinstance(value, dict):
        return {k: _filter_none(v) for k, v in value.items() if v is not None}
    return value


@dataclass
class JourneyLegStep:
    """A step of a journey leg

    """
    description_heading: Optional[str] = None
    description: Optional[str] = None
    distance: Optional[str] = None
    direction: Optional[str] = None


@dataclass
class JourneyLeg:
    """A leg of a journey

    """
    start_date_time: str
    end_date_time: str
    departure_point: str
    arrival_point: str
    mode_transport: str
    path: Optional[List[List[float]]] = None
    duration: Optional[int] = None
    instruction: Optional[str] = None
    instruction_steps: Sequence[JourneyLegStep] = None


@dataclass
class Plan:
    """A journey plan

    """
    start_date_time: str
    end_date_time: str
    legs: Sequence[JourneyLeg]
    duration: Optional[int] = None

    @property
    def n_legs(self):
        return len(self.legs)

    @property
    def modes_of_transport(self):
        return list(set([leg.mode_transport for leg in self.legs]))

    def to_dict(self):
        return _filter_none(asdict(self))

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), **kwargs)

    @property
    def field_description(self):
        def _collect_keys(dd, keys_=None):
            if keys_ is None:
                keys_ = set()
            if isinstance(dd, dict):
                for k, v in dd.items():
                    keys_.add(k)
                    _collect_keys(v, keys_)
            elif isinstance(dd, list):
                for v in dd:
                    _collect_keys(v, keys_)
            return keys_
        keys = _collect_keys(self.to_dict())
        return {k: get_description_for_field_(k) for k in keys}

    @classmethod
    def create_from_payload(cls, journey: Dict):
        """Create a Plan object from a payload

        """
        return Plan(
            start_date_time=journey.get('start_date_time'),
            end_date_time=journey.get('end_date_time'),
            duration=journey.get('duration'),
            legs=[
                JourneyLeg(
                    start_date_time=leg.get('start_date_time'),
                    end_date_time=leg.get('end_date_time'),
                    duration=leg.get('duration'),
                    instruction=leg.get('instruction'),
                    departure_point=leg.get('departure_point'),
                    arrival_point=leg.get('arrival_point'),
                    mode_transport=leg.get('mode_transport'),
                    path=leg.get('path'),
                    instruction_steps=[
                        JourneyLegStep(
                            description_heading=step.get('description_heading'),
                            description=step.get('description'),
                            direction=step.get('direction'),
                            distance=step.get('distance'),
                        ) for step in leg.get('instruction_steps', [])
                    ]
                ) for leg in journey['legs']
            ]
        )



class Planner:
    """The planner of journeys

    """
    def __init__(self,
                 planner: JourneyPlannerSearch,
                 payload_processor: JourneyPlannerSearchPayloadProcessor,
                 leg_data_to_retrieve: Sequence[Sequence[str]] = None
                 ):
        self.journey_planner = planner
        self.payload_processor = payload_processor
        self.leg_data_to_retrieve = leg_data_to_retrieve

    def make_plan(self,
                  from_loc: str,
                  to_loc: str,
                  params: JourneyPlannerSearchParams,
                  _recursive_depth: int = 0) -> Union[Plan, List[Plan]]:
        """Plan a journey between two locations, given a set of preferences and times.

        """
        payload = self.journey_planner(from_loc, to_loc, params)

        if self.journey_planner.status_code == 200:
            return [Plan.create_from_payload(journey) for journey in self.payload_processor.journeys(payload=payload)]

        elif self.journey_planner.status_code == 300:
            if _recursive_depth == 1:
                raise RuntimeError(f'Failed to disambiguate locations: {from_loc}, {to_loc}')
            _recursive_depth += 1

            self.payload_processor.disambiguate(payload)
            _from_loc = self.payload_processor.transform_loc('from', from_loc)
            _to_loc = self.payload_processor.transform_loc('to', to_loc)

            return [
                self.make_plan(
                    from_loc=locs[0],
                    to_loc=locs[1],
                    params=params,
                    _recursive_depth=_recursive_depth,
                ) for locs in itertools.product(_from_loc, _to_loc)
            ]
        else:
            raise RuntimeError(f'Unexpected status code {self.journey_planner.status_code}')


@dataclass
class Journey:
    plans: Sequence[Plan]

    @property
    def starting_point_name(self):
        return self.plans[0].legs[0].departure_point

    @property
    def destination_name(self):
        return self.plans[0].legs[-1].arrival_point

    @property
    def n_plans(self):
        return len(self.plans)

    def __getitem__(self, item):
        return self.plans[item]

    def __iter__(self):
        return iter(self.plans)

    def to_dict(self):
        return _filter_none(asdict(self))

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), **kwargs)


class JourneyMaker:
    """Constructs the journeys that fits two given locations. Multiple journeys
    are possible since the TfL API can disambiguate locations.

    """
    def __init__(self,
                 planner: Planner,
                 default_params: Optional[JourneyPlannerSearchParams] = None
                 ):
        self.planner = planner
        if default_params is None:
            default_params = JourneyPlannerSearchParams()
        self.default_params = default_params

        self.is_multiple_journeys = False
        self._journey = []

    @property
    def default_params(self):
        return self._default_params

    @default_params.setter
    def default_params(self, value):
        if not isinstance(value, JourneyPlannerSearchParams):
            raise ValueError('default_params must be an instance of JourneyPlannerSearchParams')
        self._default_params = value

    def __getitem__(self, item):
        return self._journey[item]

    def __len__(self):
        return len(self._journey)

    @property
    def payload_description(self):
        return self.planner.payload_processor.payload_description

    def make_journey(self,
                     starting_point: str,
                     destination: str,
                     **kwargs):
        """Make a journey between two locations

        """
        _params = self.default_params.model_copy(update=kwargs)

        plans = self.planner.make_plan(
            from_loc=starting_point,
            to_loc=destination,
            params=_params,
        )
        if isinstance(plans, list):
            if isinstance(plans[0], list):
                self.is_multiple_journeys = True
            else:
                self.is_multiple_journeys = False
                plans = [plans]

        self._journey.extend([Journey(plans=_plans) for _plans in plans])
