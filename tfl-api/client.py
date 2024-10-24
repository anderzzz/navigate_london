"""Client to interact with the Transport for London Unified API.

Anders Ohrn, 2024 Oct

"""
from typing import Optional, Dict
import requests

_BASE_URL = 'https://api.tfl.gov.uk/'


class TFLClient:
    """Bla bla

    """
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get(self, endpoint, params: Optional[Dict[str, str]] = None):
        """Get data from the TFL API, using the given endpoint and parameters.

        """
        if params is None:
            params = {'app_id': self.app_id, 'app_key': self.app_key}
        else:
            params.update({'app_id': self.app_id, 'app_key': self.app_key})

        response = requests.get(f'{_BASE_URL}{endpoint}', params=params)
        response.raise_for_status()

        return response.json()
