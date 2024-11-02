"""Map creations

"""
import os
from typing import List
import itertools
import folium
import seaborn as sns
import ast
import webbrowser

from base import ToolSet
from navigator import Plan, JourneyMaker

TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class MapDrawer:
    """Bla bla

    """
    def __init__(self,
                 color_palette: str = 'tab10',
                 ):
        self._color_cycle = itertools.cycle(sns.color_palette(color_palette))
        self.m = folium.Map()

    def get_color(self):
        return '#{:02x}{:02x}{:02x}'.format(*[int(c * 255) for c in next(self._color_cycle)])

    def make_map_for_plan(self, plan: Plan):
        for leg in plan.legs:
            print (leg.path)
            try:
                path = ast.literal_eval(leg.path)
            except ValueError:
                break

            folium.PolyLine(
                path,
                color=self.get_color(),
                weight=3,
            ).add_to(self.m)

        self.m.fit_bounds(self.m.get_bounds())

    def save_map(self, file_path: str):
        self.m.save(file_path)

    def display_map(self, file_path: str):
        self.save_map(file_path)
        webbrowser.open('file://' + os.path.realpath(file_path))


class MapDrawerToolSet(ToolSet):
    """Bla bla

    """
    def __init__(self,
                 drawer: MapDrawer,
                 maker: JourneyMaker,
                 tools_to_include: List[str] = None,
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
