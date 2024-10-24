"""Management of the Transport for London API.

Anders Ohrn, 2024 Oct

"""
import os
from typing import Optional, Dict
from pydantic import BaseModel, Field, field_validator, root_validator
import datetime
import re
import requests

_URL_ROOT_TFL_API = 'https://api.tfl.gov.uk'


class JourneyPlannerParams(BaseModel):
    from_location: str = Field(alias='from')
    to: str

    via: Optional[str] = None
    national_search: Optional[bool] = Field(None, alias='nationalSearch')
    date: Optional[str] = None
    time: Optional[str] = None
    time_is: Optional[str] = Field(None, alias='timeIs')


    @field_validator('from_location', 'to', 'via')
    @classmethod
    def validate_location(cls, value, field):
        if value is None:
            return value

        # WGS84 coordinates pattern (lat,long)
        coord_pattern = r'^-?\d+\.?\d*,-?\d+\.?\d*$'

        # UK postcode pattern (basic validation)
        postcode_pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'

        # Naptan ID pattern (based on common format)
        naptan_pattern = r'^[0-9]{12}$'

        # ICS StopId pattern (you might need to adjust this based on actual format)
        ics_pattern = r'^[A-Z0-9]+$'

        # Check if it matches any of the allowed formats
        if (re.match(coord_pattern, value) or
            re.match(postcode_pattern, value.upper()) or
            re.match(naptan_pattern, value) or
            re.match(ics_pattern, value)):
            return value

        # If none of the above, accept as free-text string
        return value

@field_validator('date')
def validate_date(cls, v):
    if v is None:
        return v
    try:
        # Validate date format (yyyyMMdd)
        datetime.strptime(v, '%Y%m%d')
        return v
    except ValueError:
        raise ValueError('date must be in yyyyMMdd format')

@field_validator('time')
def validate_time(cls, v):
    if v is None:
        return v
    try:
        # Validate time format (HHmm)
        if not re.match(r'^[0-2][0-9][0-5][0-9]$', v):
            raise ValueError
        hour = int(v[:2])
        minute = int(v[2:])
        if hour >= 24 or minute >= 60:
            raise ValueError
        return v
    except ValueError:
        raise ValueError('time must be in HHmm format (24-hour)')

@validator('time_is')
def validate_time_is(cls, v):
    if v is None:
        return v
    valid_values = ['departing', 'arriving']
    if v not in valid_values:
        raise ValueError(f'timeIs must be one of: {", ".join(valid_values)}')
    return v

        # Root validator to check time-related fields consistency
        @root_validator
        def check_time_fields(cls, values):
            time = values.get('time')
            time_is = values.get('time_is')

            # If time is provided, timeIs should also be provided
            if time is not None and time_is is None:
                raise ValueError('timeIs must be provided when time is specified')

            # If timeIs is provided, time should also be provided
            if time_is is not None and time is None:
                raise ValueError('time must be provided when timeIs is specified')

            return values

        class Config:
            allow_population_by_field_name = True  # Allows using both alias and field names


class TFLAPIClient:
    """Bla bla

    """
    def __init__(self,
                 app_key_env_var: str,
                 app_id_env_var: str,
                 ):
        app_key = os.getenv(app_key_env_var)
        app_id = os.getenv(app_id_env_var)
        self.headers = {
            'Authorization': f'AppKey {app_key}',
            'Content-Type': 'application/json'
        }
        self.app_key = app_key
        self.app_id = app_id

    def _execute(self, endpoint: str, params: Optional[Dict[str, str]] = None):
        url = f'{_URL_ROOT_TFL_API}/{endpoint}'
        response = requests.get(
            url=url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def journey_planner(self,
                        from_loc: str,
                        to_loc: str,
                        via_loc: Optional[str] = None,
                        date: Optional[str] = None,
                        time: Optional[str] = None,
                        time_is: Optional[str] = None,
                        ):
