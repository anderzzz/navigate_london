"""

"""
from tfl_api import (
    TFLClient,
    SearchStopPoints,
    JourneyModesAvailable,
    Modes
)

client = TFLClient(env_var_app_key='TFL_API_KEY')
api_modes = JourneyModesAvailable(client)
print(api_modes())
stops = SearchStopPoints(client)
print(stops('london bridge', modes=[Modes.TUBE, Modes.BUS]))
