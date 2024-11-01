"""Map creations

"""
from typing import List
import itertools
import folium
import seaborn as sns
import ast

from navigator import Plan


class MapDrawer:
    """Bla bla

    """
    def __init__(self,
                 color_palette: str = 'tab10',
                 ):
        self._color_cycle = itertools.cycle(sns.color_palette(color_palette))
        #self._color_cycle = iter(['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'])
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
