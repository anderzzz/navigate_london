"""Bla bla

"""
from tfl_api import (
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)


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
                  **params):
        """Plan a journey between two locations, given a set of preferences and times.

        """
        payload = self.journey_planner(from_loc, to_loc, **params)

        if self.journey_planner.status_code in [200, 300]:
            return self.payload_processor(payload)
        else:
            raise RuntimeError(f'Unexpected status code {self.journey_planner.status_code}')
