"""Engine to interact with Anthropic's API.

"""
import os
from typing import Optional, Dict, Any

from anthropic import Anthropic


class Engine:
    """Bla bla

    """
    def __init__(self,
                 api_key_env_var: str,
                 system_prompt: str,
                 tools: Optional[Dict[str, Any]] = None
                 ):
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f'Did not find an API key in environment variable {api_key_env_var}')
        self.client = Anthropic(api_key=os.getenv(api_key_env_var))
        self.system_prompt = system_prompt

    def process(self,
                input_prompt: str,
                use_tool: Optional[str] = None,
                respond_to_tool: Optional[bool] = False,
                ):
        """Bla bla

        """
        pass
