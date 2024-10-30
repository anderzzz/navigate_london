"""Engine to interact with Anthropic's API.

"""
import os
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field

from anthropic import Anthropic


@dataclass
class AnthropicMessageParams:
    model: str
    max_tokens: int
    temperature: float = 0.7


class Message(BaseModel):
    role: Literal['user', 'tool', 'assistant']
    content: str
    tool: Optional[str] = None


class MessageStack(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    def add_message(self, role: str, content: str, tool: Optional[str] = None):
        self.messages.append(Message(role=role, content=content, tool=tool))

    def to_list_dicts(self):
        return [message.model_dump() for message in self.messages]


class Engine:
    """Bla bla

    """
    def __init__(self,
                 api_key_env_var: str,
                 system_prompt: str,
                 message_params: AnthropicMessageParams,
                 tools: Optional[List[Dict[str, Any]]] = None,
                 ):
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f'Did not find an API key in environment variable {api_key_env_var}')
        self.client = Anthropic(api_key=os.getenv(api_key_env_var))
        self.system_prompt = system_prompt
        self.message_params = message_params
        if tools is None:
            tools = []
        self.tools = tools

        self._message_stack = MessageStack()

    def process(self,
                input_prompt: str,
                tool_choice: str = 'auto',
                ):
        """Bla bla

        """
        self._message_stack.add_message(
            role='user',
            content=input_prompt,
        )
        response = self.client.messages.create(
            system=self.system_prompt,
            model=self.message_params.model,
            max_tokens=self.message_params.max_tokens,
            temperature=self.message_params.temperature,
            tool_choice=tool_choice,
        )

        self._message_stack.add_message(
            role='assistant',
            content=response['message'],
            tool=response['tool'],
        )
