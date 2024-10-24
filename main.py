"""

"""
from tfl_api import (
    TFLClient,
    SearchStopPoints,
    JourneyModesAvailable,
)

client = TFLClient(env_var_app_key='TFL_API_KEY')
api_modes = JourneyModesAvailable(client)
print(api_modes())
