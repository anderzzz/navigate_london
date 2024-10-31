"""Agents that define an engine with system prompt and optional tools

"""
from typing import Optional, Dict
from jinja2 import Environment, FileSystemLoader

from base import ToolSet
from semantics import Engine, AnthropicMessageParams
from navigator import Planner, JourneyMaker, JourneyMakerToolSet
from tfl_api import (
    TFLClient,
    JourneyPlannerSearchParams,
    JourneyPlannerSearch,
    JourneyPlannerSearchPayloadProcessor,
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
tools_journey_maker = JourneyMakerToolSet(maker=maker)


def build_agent(
        api_key_env_var: str,
        system_prompt_template: str,
        model_name: str,
        max_tokens: int,
        temperature: float,
        tools: Optional[ToolSet] = None,
        system_prompt_kwargs: Optional[Dict] = None,
):
    system_prompt_template = Environment(
        loader=FileSystemLoader('./prompt_templates'),
    ).get_template(system_prompt_template)
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


agent_handle_preferences_and_settings = build_agent(
    api_key_env_var='ANTHROPIC_API_KEY',
    system_prompt_template='preferences_and_settings.j2',
    model_name='claude-3-5-sonnet-20241022',
    max_tokens=1000,
    temperature=0.7,
    tools=tools_journey_maker,
)