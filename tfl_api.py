"""Management of the Transport for London API.

Anders Ohrn, 2024 Oct

"""
from typing import Optional, Dict
import os
import requests

_URL_ROOT_TFL_API = 'https://api.tfl.gov.uk'


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
