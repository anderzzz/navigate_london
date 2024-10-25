"""

"""
from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
)
from navigator import (
    Planner,
    Plan,
)

client = TFLClient(env_var_app_key='TFL_API_KEY')
planner = Planner(
    tfl_journey_planner=JourneyPlannerSearch(client),
    matching_threshold=900.0,
)
params = JourneyPlannerSearchParams(
    date='20241026',
    time='0800',
    time_is='departing',
)
x = planner.make_plan(
    from_loc='Hyde Park Corner',
    to_loc='London Bridge',
    **params.model_dump(),
)
print (x)
