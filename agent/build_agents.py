"""The main place where agents are created and configured.

"""
import os
from typing import Optional, Dict
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import pytz

from agent.tools import SubTaskAgentToolSet
from base import ToolSet
from user import user_0
from semantics import Engine, AnthropicMessageParams
from navigator import Planner, JourneyMaker, JourneyMakerToolSet
from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
)
from artefacts import (
    MapDrawer,
    CalendarEventMakerForPlan,
    OutputArtefactsToolSet,
)


PROMPT_FOLDER = os.path.join(os.path.dirname(__file__), 'prompt_templates')


def build_agent(
        api_key_env_var: str,
        system_prompt_template: str,
        model_name: str,
        max_tokens: int,
        temperature: float,
        name: str,
        tools: Optional[ToolSet] = None,
        system_prompt_kwargs: Optional[Dict] = None,
) -> Engine:
    """Build an agent with a system prompt and optional tools

    Args:
        api_key_env_var: The name of the environment variable that holds the API key to the LLM API
        system_prompt_template: The name of the Jinja2 template file with the system prompt
        model_name: The name of the LLM model to use for the agent
        max_tokens: The maximum number of tokens to generate
        temperature: The temperature to use for generation
        name: The name of the agent, used for logging
        tools: The tool set to include with the agent
        system_prompt_kwargs: The keyword arguments to pass to the system prompt template in case the
            jinja template includes variables

    """
    system_prompt_template = Environment(
        loader=FileSystemLoader(PROMPT_FOLDER),
    ).get_template(system_prompt_template)
    if system_prompt_kwargs is None:
        system_prompt_kwargs = {}

    return Engine(
        name=name,
        api_key_env_var=api_key_env_var,
        system_prompt=system_prompt_template.render(**system_prompt_kwargs),
        message_params=AnthropicMessageParams(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
        ),
        tools=tools,
    )


#
# Instantiate the core components of tools to be used by the agents.
tfl_client = TFLClient(env_var_app_key='TFL_API_KEY')
planner = Planner(
    planner=JourneyPlannerSearch(tfl_client),
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
maker = JourneyMaker(
    planner=planner,
    default_params=JourneyPlannerSearchParams(
        walking_speed='fast',
        time_is='arriving',
    )
)
map_drawer = MapDrawer()
calendar_maker = CalendarEventMakerForPlan(
    file_path=os.path.join(os.path.dirname(__file__), 'calendar_event.ics'),
    default_event_name='Generated Journey Plan',
)


#
# Instantiate the various sub-task agents, which are forms of LLM engines.
agent_handle_preferences_and_settings = build_agent(
    name='agent to handle preference settings',
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='preferences_and_settings.j2',
    model_name='claude-3-haiku-20240307',
    max_tokens=1000,
    temperature=0.1,
    tools=JourneyMakerToolSet(
        maker=maker,
        tools_to_include=('set_default_journey_parameters',),
    )
)
agent_handle_journey_plans = build_agent(
    name='agent to compute journey plans',
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='journey_plans.j2',
    system_prompt_kwargs=user_0.get('user location short-hands', None),
    model_name='claude-3-haiku-20240307',
    max_tokens=1000,
    temperature=0.1,
    tools=JourneyMakerToolSet(
        maker=maker,
        tools_to_include=('compute_journey_plans',
                          'get_computed_journey',
                          'get_computed_journey_plan'),
    )
)
agent_handle_output_artefacts = build_agent(
    name='agent to generate output artifacts',
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='output_artefacts.j2',
    model_name='claude-3-5-sonnet-20241022',
#    model_name='claude-3-haiku-20240307',
    max_tokens=1000,
    temperature=0.1,
    tools=OutputArtefactsToolSet(
        drawer=map_drawer,
        calendar_maker=calendar_maker,
        maker=maker,
        tools_to_include=('draw_map_for_plan',
                          'create_ics_file_for_plan',
                          'get_computed_journey',
                          'get_computed_journey_plan'),
    )
)


#
# Instantiate the agent that will route requests to the appropriate sub-task agent as well as
# speak with the principal.
date_now_in_london = datetime.now(pytz.timezone('Europe/London'))
date_str = date_now_in_london.strftime('%Y-%m-%d')
agent_router = build_agent(
    name='agent to route requests and speak with the principal',
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='router.j2',
    system_prompt_kwargs={
        'year_today': '2024',
        'date_today': date_str,
        'user_name': user_0.get('name', None),
        'user_shorthands': user_0.get('user location short-hands', None),
    },
    model_name='claude-3-5-sonnet-20241022',
    max_tokens=1000,
    temperature=0.5,
    tools=SubTaskAgentToolSet(
        subtask_agents={
            'preferences_and_settings': agent_handle_preferences_and_settings,
            'journey_planner': agent_handle_journey_plans,
            'output_artefacts': agent_handle_output_artefacts,
        },
        tools_to_include=('preferences_and_settings',
                          'journey_planner',
                          'output_artefacts'),
    ),
)
