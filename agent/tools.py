"""Bla bla

"""
import os
from optparse import Option
from typing import Optional, Sequence

from base import ToolSet
from .agents import build_agent

TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class HelperAgentToolSet(ToolSet):
    """Bla bla

    """
    def __init__(self,
                 tools_to_include=Optional[Sequence[str]],
                 tool_spec_file: str = TOOL_SPEC_FILE,
                 ):
        super().__init__(tool_spec_file, tools_to_include)

    def handle_preferences_and_settings(self):
