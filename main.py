"""

"""
from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
)

client = TFLClient(env_var_app_key='TFL_API_KEY')
params = JourneyPlannerSearchParams(
    date='20241026',
    time='0800',
    time_is='departing',
)
search = JourneyPlannerSearch(client)
x = search(
    from_loc='Hyde Park Corner',
    to_loc='London Bridge',
    **params.model_dump(),
)
print (x)
