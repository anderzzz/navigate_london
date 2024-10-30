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
    JourneyMaker,
    JourneyMakerTools,
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
#    cycle_preference='allTheWay',
)
maker = JourneyMaker(planner=planner, default_params=params)
#maker.make_journey(
#    starting_point='490000119F',
#    destination='490000040A',
#    date='20241028',
#    time='1840',
#)
#print (maker[0][0].to_json(indent=4))
#print (maker[0][0].field_description)
tools = JourneyMakerTools(maker=maker)
p = tools.compute_journey_plans(
    starting_point='490000119F',
    destination='490000040A',
    date='20241108',
    time='1840',
)
print (p)
p = tools.get_computed_journey(0)
print (p)


