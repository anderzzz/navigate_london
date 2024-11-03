"""Bla bla

"""
import os
from typing import Sequence

from base import ToolSet
from navigator import JourneyMaker
from .maps import MapDrawer


TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class OutputArtefactsToolSet(ToolSet):
    """Bla bla

    """
    def __init__(self,
                 drawer: MapDrawer,
                 maker: JourneyMaker,
                 tools_to_include: Sequence[str] = None,
                 tool_spec_file: str = TOOL_SPEC_FILE,
                 ):
        super().__init__(tools_to_include=tools_to_include, tool_spec_file=tool_spec_file)
        self.drawer = drawer
        self.journey_maker = maker

    def draw_map_for_plan(self, journey_index: int, plan_index: int, browser_display: bool=True) -> str:
        self.drawer.make_map_for_plan(self.journey_maker[journey_index][plan_index])
        self.drawer.save_map('temp.html')
        ret_message = 'Map created and saved to temp.html.'
        if browser_display:
            self.drawer.display_map('temp.html')
            ret_message += ' Browser opened with map.'

        return ret_message
