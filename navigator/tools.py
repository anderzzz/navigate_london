"""Functions that define tools interacting with the planner

"""
import os
from typing import Dict, Any, Sequence, Optional, List
import json

from base import ToolSet
from tfl_api import JourneyPlannerSearchParams
from .planner import JourneyMaker

TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class JourneyMakerToolSet(ToolSet):
    """Bla bla

    """
    def __init__(self,
                 maker: JourneyMaker,
                 tools_to_include: Optional[Sequence[str]] = None,
                 tool_spec_file: str = TOOL_SPEC_FILE,
             ):
        super().__init__(tool_spec_file, tools_to_include)
        self.maker = maker

    def set_default_journey_params(self, **kwargs) -> str:
        self.maker.default_params = JourneyPlannerSearchParams(**kwargs)
        return 'Successfully applied the following update to default journey parameters:\n' + json.dumps(
            kwargs,
            indent=4,
        )

    def compute_journey_plans(self,
                              starting_point: str,
                              destination: str,
                              **kwargs) -> str:
        self.maker.make_journey(
            starting_point=starting_point,
            destination=destination,
            **kwargs,
        )
        return json.dumps({
            'number of journeys planned': len(self.maker),
            'journey meta data': [
                {
                    'journey index': k,
                    'starting point': journey.starting_point_name,
                    'destination': journey.destination_name,
                    'number of plans': journey.n_plans,
                } for k, journey in enumerate(self.maker)
            ]
        },
            indent=4,
        )

    def get_computed_journey(self, journey_index: int) -> str:
        return self.maker[journey_index].to_json(indent=4)

    def get_computed_journey_plan(self, journey_index: int, plan_index: int) -> str:
        return self.maker[journey_index][plan_index].to_json(indent=4)

    def get_plan_field_description(self):
        return self.maker[0][0].field_description
