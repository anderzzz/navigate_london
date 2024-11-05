"""Client to interact with the Transport for London Unified API.

Anders Ohrn, 2024 Oct

"""
import os
from typing import Optional, Dict
import requests

_BASE_URL_TFL = 'https://api.tfl.gov.uk/'


class TFLClient:
    """Basic client to interact with the TFL API.

    Args:
        env_var_app_key: The name of the environment variable that holds the app key for the TFL API

    """
    def __init__(self, env_var_app_key):
        self.app_key = os.getenv(env_var_app_key)
        if self.app_key is None:
            raise ValueError(f'Did not find an app key in environment variable {env_var_app_key}')

    def get(self, endpoint, params: Optional[Dict[str, str]] = None):
        """Get data from the TFL API, using the given endpoint and parameters.

        """
        if params is None:
            params = {'app_key': self.app_key}
        else:
            params.update({'app_key': self.app_key})

        for key, value in params.items():
            if isinstance(value, list):
                params[key] = ','.join(value)

        response = requests.get(f'{_BASE_URL_TFL}{endpoint}', params=params)
        response.raise_for_status()

        return response.status_code, response.json()
