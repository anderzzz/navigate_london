"""Bla bla

"""
from dataclasses import dataclass
import itertools

from tfl_api import (
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)


@dataclass
class Plan:
    """A journey plan

    """
    foobar: str


class Planner:
    """The planner of journeys

    """
    def __init__(self,
                 planner: JourneyPlannerSearch,
                 payload_processor: JourneyPlannerSearchPayloadProcessor,
                 ):
        self.journey_planner = planner
        self.payload_processor = payload_processor

    def make_plan(self,
                  from_loc: str,
                  to_loc: str,
                  _recursive_depth: int = 0,
                  **params):
        """Plan a journey between two locations, given a set of preferences and times.

        """
        payload = self.journey_planner(from_loc, to_loc, **params)

        if self.journey_planner.status_code == 200:
            return Plan(**self.payload_processor.process(payload))

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
