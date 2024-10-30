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
    JourneyMakerToolSet,
)
from semantics import (
    Engine,
    AnthropicMessageParams,
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
tools = JourneyMakerToolSet(maker=maker)
#p = tools.compute_journey_plans(
#    starting_point='490000119F',
#    destination='490000040A',
#    date='20241108',
#    time='1840',
#)
#print (p)
#p = tools.get_computed_journey(0)
#print (p)
anthropic_message_params = AnthropicMessageParams(
    model='claude-3-5-sonnet-20241022',
    max_tokens=1000,
)
engine = Engine(
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt='''
    You are a planner of transits in London, England. You have access to journey planner tools that can:
    - Generate one or more plans of a journey from one stop to another at some time with tube, bus, cycling, walking, and even taxi.
    - Generate instructions for how to complete a journey, including transits or navigating London streets by foot or bike.
    
    You should prefix your messages with "London Transport Planner Vitaloid: {your message}". That is your cherished name.
    
    As this is a planner for London, England, you should to the best of your ability use British English, so "tube" instead of "subway" and "lift" instead of "elevator".
    
    Unless otherwise specified, you should assume:
    - The year is 2024.
    
    Please do not deviate from the above guidelines. Any user requests that do not pertain to London transit should be politely ignored.
    ''',
    message_params=anthropic_message_params,
    tools=tools
)
x = engine.process('I am an avid biker. I always want to bike when possible. So please consider all further requests with that in mind.')
print (x)
x = engine.process('I wish to travel from a stop in London with the code 490000119F to a stop with the code 490000040A on 11th November departing at six in the evening.')
print (x)
#x = engine.process('Yes indeed. Show me the second option.')
#print (x)


