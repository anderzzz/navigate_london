"""The tool set for the router agent, which enables it to use the sub-task agents as tools.

"""
import os
from typing import Optional, Sequence, Dict, Any

from base import ToolSet
from semantics import Engine

TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class SubTaskAgentToolSet(ToolSet):
    """Sub-task agent tool set

    Args:
        subtask_agents: The sub-task agents to use as tools
        tools_to_include: The tools to include in the tool set
        tool_spec_file: The file with the tool specifications

    """
    def __init__(self,
                 subtask_agents: Dict[str, Engine],
                 tools_to_include=Optional[Sequence[str]],
                 tool_spec_file: str = TOOL_SPEC_FILE,
                 ):
        super().__init__(tool_spec_file, tools_to_include)
        self.subtask_agents = subtask_agents

        # The sub-task agents are only going to create (with LLM) and execute a call to the underlying tool
        # function, not create any conversational output or recall previous outputs.
        self.kwargs_only_use_tool_no_memory = {
            'tool_choice_type': 'any',
            'interpret_tool_use_output': False,
            'with_memory': False,
        }

    def _invoke_engine(self, agent_key: str, **kwargs) -> str:
        return self.subtask_agents[agent_key].process(**kwargs)

    def preferences_and_settings(self,
                                 input_prompt: str,
                                 ) -> str:
        return self._invoke_engine('preferences_and_settings',
                                   input_prompt=input_prompt,
                                   **self.kwargs_only_use_tool_no_memory
                                   )

    def journey_planner(self, input_prompt: str) -> str:
        return self._invoke_engine('journey_planner',
                                   input_prompt=input_prompt,
                                   **self.kwargs_only_use_tool_no_memory
                                   )

    def output_artefacts(self, input_prompt: str, input_structured: Dict[str, Any]) -> str:
        return self._invoke_engine('output_artefacts',
                                   input_prompt=input_prompt,
                                   input_structured=input_structured,
                                   **self.kwargs_only_use_tool_no_memory
                                   )
