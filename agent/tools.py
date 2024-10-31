"""Bla bla

"""
import os
from typing import Optional, Sequence, Dict

from base import ToolSet
from semantics import Engine

TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class SubTaskAgentToolSet(ToolSet):
    """Bla bla

    """
    def __init__(self,
                 subtask_agents: Dict[str, Engine],
                 tools_to_include=Optional[Sequence[str]],
                 tool_spec_file: str = TOOL_SPEC_FILE,
                 ):
        super().__init__(tool_spec_file, tools_to_include)
        self.subtask_agents = subtask_agents

    def _invoke_engine(self, agent_key: str, **kwargs) -> str:
        return self.subtask_agents[agent_key].process(**kwargs)

    def preferences_and_settings(self, **kwargs) -> str:
        return self._invoke_engine('preferences_and_settings', **kwargs)

    def journey_planner(self, **kwargs) -> str:
        return self._invoke_engine('journey_planner', **kwargs)

