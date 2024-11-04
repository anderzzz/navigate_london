"""Create calendar events

"""
from typing import Optional, Sequence
from ics import Calendar, Event
from datetime import datetime

from navigator.planner import Plan


class CalendarEventMakerForPlan:
    """Make calendar events for plans

    """
    def __init__(self,
                 file_path: str,
                 default_event_name: str,
                 ):
        self.file_path = file_path
        self.event_name = default_event_name

    def __call__(self,
                 plan: Plan,
                 description: str,
                 event_name: Optional[str] = None,
                 file_attachments: Optional[Sequence[str]] = None,
                 ):
        c = Calendar()
        e = Event()

#        dt_start = datetime.strptime(plan.start_date_time, '%Y%m%dT%H:%M:%S')
#        dt_end = datetime.strptime(plan.end_date_time, '%Y%m%dT%H:%M:%S')

        e.begin = plan.start_date_time
        e.end = plan.end_date_time

        e.name = event_name or self.event_name
        e.description = description

        if file_attachments is not None:
            if len(file_attachments) > 1:
                raise NotImplementedError('Multiple file attachments not supported yet')

            for file_attachment in file_attachments:
                with open(file_attachment, 'rb') as f:
                    e.attach = f.read()

        c.events.add(e)
        with open(self.file_path, 'w') as f:
            f.writelines(c)

        return True
