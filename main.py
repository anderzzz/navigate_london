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
        matching_threshold=950.0,
        leg_data_to_retrieve=(
            'start of leg, date and time',
            'end of leg, date and time',
            'mode of transport',
        ),
    ),
)
params = JourneyPlannerSearchParams(
    date='20241028',
    time='0800',
    time_is='departing',
)
x = planner.make_plan(
    from_loc='490000119F',
    to_loc='London Bridge',
    **params.model_dump(),
)
print (x)
