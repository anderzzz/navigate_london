"""Output artifacts tool set.

"""
import os
from typing import Sequence, Optional

from base import ToolSet
from navigator import JourneyMaker
from .maps import MapDrawer
from .calendar import CalendarEventMakerForPlan


TOOL_SPEC_FILE = os.path.join(os.path.dirname(__file__), 'tools.json')


class OutputArtefactsToolSet(ToolSet):
    """Given that a journey has been computed, this tool set provides means to output artefacts.

    The journey data is available from the `JourneyMaker` object and requires two indices to access.

    """
    def __init__(self,
                 maker: JourneyMaker,
                 drawer: Optional[MapDrawer] = None,
                 calendar_maker: Optional[CalendarEventMakerForPlan] = None,
                 tools_to_include: Sequence[str] = None,
                 tool_spec_file: str = TOOL_SPEC_FILE,
                 ):
        super().__init__(tools_to_include=tools_to_include, tool_spec_file=tool_spec_file)
        self.drawer = drawer
        self.calendar_maker = calendar_maker
        self.journey_maker = maker

    def draw_map_for_plan(self, journey_index: int, plan_index: int, browser_display: bool=True) -> str:
        if self.drawer is None:
            raise ValueError('Map drawer not set, cannot draw map.')

        self.drawer.make_map_for_plan(self.journey_maker[journey_index][plan_index])
        self.drawer.save_map('temp.html')
        ret_message = 'Map created and saved to temp.html.'
        if browser_display:
            self.drawer.display_map('temp.html')
            ret_message += ' Browser opened with map.'

        return ret_message

    def create_ics_file_for_plan(self,
                                 journey_index: int,
                                 plan_index: int,
                                 description: str,
                                 event_name: Optional[str] = None,
                                 file_attachments: Optional[Sequence[str]] = None,
                                 ) -> str:
        if self.calendar_maker is None:
            raise ValueError('Calendar event maker not set, cannot create calendar event.')

        plan = self.journey_maker[journey_index][plan_index]
        self.calendar_maker(plan, description, event_name, file_attachments)
        return f'ICS file created, see {self.calendar_maker.file_path}'

    def get_computed_journey(self, journey_index: int) -> str:
        return self.journey_maker[journey_index].to_json(indent=4)

    def get_computed_journey_plan(self, journey_index: int, plan_index: int) -> str:
        return self.journey_maker[journey_index][plan_index].to_json(indent=4)
