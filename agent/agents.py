"""Agents that define an engine with system prompt and optional tools

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
    MapDrawerToolSet,
)


PROMPT_FOLDER = os.path.join(os.path.dirname(__file__), 'prompt_templates')


def build_agent(
        api_key_env_var: str,
        system_prompt_template: str,
        model_name: str,
        max_tokens: int,
        temperature: float,
        tools: Optional[ToolSet] = None,
        system_prompt_kwargs: Optional[Dict] = None,
):
    """Build an agent with a system prompt and optional tools"""
    system_prompt_template = Environment(
        loader=FileSystemLoader(PROMPT_FOLDER),
    ).get_template(system_prompt_template)
    if system_prompt_kwargs is None:
        system_prompt_kwargs = {}
    return Engine(
        api_key_env_var=api_key_env_var,
        system_prompt=system_prompt_template.render(**system_prompt_kwargs),
        message_params=AnthropicMessageParams(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
        ),
        tools=tools,
    )


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


agent_handle_preferences_and_settings = build_agent(
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='preferences_and_settings.j2',
    model_name='claude-3-haiku-20240307',
    max_tokens=1000,
    temperature=0.7,
    tools=JourneyMakerToolSet(
        maker=maker,
        tools_to_include=('set_default_journey_parameters',),
    )
)
agent_handle_journey_plans = build_agent(
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='journey_plans.j2',
    system_prompt_kwargs=user_0['user location short-hands'],
    model_name='claude-3-haiku-20240307',
    max_tokens=1000,
    temperature=0.7,
    tools=JourneyMakerToolSet(
        maker=maker,
        tools_to_include=('compute_journey_plans',
                          'get_computed_journey',
                          'get_computed_journey_plan'),
    )
)
agent_handle_map_drawer = build_agent(
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='map_drawer.j2',
    model_name='claude-3-haiku-20240307',
    max_tokens=1000,
    temperature=0.7,
    tools=MapDrawerToolSet(
        drawer=map_drawer,
        maker=maker,
        tools_to_include=('draw_map_for_plan',),
    )
)


date_now_in_london = datetime.now(pytz.timezone('Europe/London'))
date_str = date_now_in_london.strftime('%Y-%m-%d')
agent_router = build_agent(
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='router.j2',
    system_prompt_kwargs={
        'year_today': '2024',
        'date_today': date_str,
        'user_name': user_0.get('name', None),
    },
    model_name='claude-3-5-sonnet-20241022',
    max_tokens=1000,
    temperature=0.7,
    tools=SubTaskAgentToolSet(
        subtask_agents={
            'preferences_and_settings': agent_handle_preferences_and_settings,
            'journey_planner': agent_handle_journey_plans,
            'output_artefacts': agent_handle_map_drawer,
        },
        tools_to_include=('preferences_and_settings', 'journey_planner', 'output_artefacts'),
    ),
)
