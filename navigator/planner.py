"""Bla bla

"""
from typing import Sequence, Dict, Optional
from dataclasses import dataclass
import itertools

from tfl_api import (
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)


@dataclass
class JourneyLeg:
    """A leg of a journey

    """
    start_date_time: str
    end_date_time: str
    departure_point: str
    arrival_point: str
    mode_transport: str
    duration: Optional[int] = None
    instruction: Optional[str] = None


@dataclass
class Plan:
    """A journey plan

    """
    start_date_time: str
    end_date_time: str
    legs: Sequence[JourneyLeg]
    duration: Optional[int] = None

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
                    mode_transport=leg.get('mode_transport')
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
                  _recursive_depth: int = 0,
                  **params):
        """Plan a journey between two locations, given a set of preferences and times.

        """
        payload = self.journey_planner(from_loc, to_loc, **params)

        if self.journey_planner.status_code == 200:
            return [Plan.create_from_payload(journey) for journey in self.payload_processor.journeys(payload=payload)]

        elif self.journey_planner.status_code == 300:
            if _recursive_depth == 1:
                raise RuntimeError(f'Failed to disambiguate locations: {from_loc}, {to_loc}')
            _recursive_depth += 1

            self.payload_processor.disambiguate(payload)
            _from_loc = self.payload_processor.transform_loc('from', from_loc)
            _to_loc = self.payload_processor.transform_loc('to', to_loc)
            _via_loc = self.payload_processor.transform_loc('via', params['via'])

            return [
                self.make_plan(
                    from_loc=locs[0],
                    to_loc=locs[1],
                    via_loc=locs[2],
                    _recursive_depth=_recursive_depth,
                    **params
                ) for locs in itertools.product(_from_loc, _to_loc, _via_loc)
            ]
        else:
            raise RuntimeError(f'Unexpected status code {self.journey_planner.status_code}')
