"""

"""
from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)
from navigator import (
    Planner,
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
            'duration',
            'instruction',
        ),
    ),
)
params = JourneyPlannerSearchParams(
    date='20241028',
    time='1800',
    time_is='departing',
)
x = planner.make_plan(
    from_loc='490000119F',
    to_loc='London Bridge',
    **params.model_dump(),
)
print (x)
