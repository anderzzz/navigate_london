"""Bla bla

"""
from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)
from navigator import (
    Planner,
    JourneyMaker,
    JourneyMakerToolSet,
)
from artefacts import (
    MapDrawer,
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
            'instruction',
            'instruction_steps',
            'path',
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
)
maker = JourneyMaker(planner=planner, default_params=params)
tools = JourneyMakerToolSet(maker=maker)

maker.make_journey(
    date='20241111',
    time='0800',
    starting_point='490000119F',
    destination='490000040A'
)
drawer = MapDrawer()
xx = maker[0][0]
print (xx)
drawer.make_map_for_plan(xx)
print (drawer.m)
drawer.m.save('test.html')

