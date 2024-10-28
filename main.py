"""

"""
import json
from dataclasses import asdict

from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)
from navigator import (
    Planner,
    JourneyMaker,
)

client = TFLClient(env_var_app_key='TFL_API_KEY')
planner = Planner(
    planner=JourneyPlannerSearch(client),
    payload_processor=JourneyPlannerSearchPayloadProcessor(
        matching_threshold=990.0,
        leg_data_to_retrieve=(
            'start_date_time',
            'end_date_time',
            'mode_transport',
            'departure_point',
            'arrival_point',
#            'duration',
            'instruction',
            'instruction_steps',
        ),
        step_data_to_retrieve=(
            'description',
            'description_heading',
        ),
    ),
)
params = JourneyPlannerSearchParams(
    walking_speed='fast',
    time_is='arriving',
    cycle_preference='allTheWay',
)
maker = JourneyMaker(planner=planner, default_params=params)
x = maker.make_journey(
    starting_point='490000119F',
    destination='490000040A',
    date='20241028',
    time='1840',
)
print (json.dumps(asdict(x[0]), indent=4))
