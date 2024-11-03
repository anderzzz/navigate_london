"""Engine to interact with Anthropic's API.

"""
import os
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field
import json

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock, MessageParam, ToolResultBlockParam

from base import ToolSet


@dataclass
class AnthropicMessageParams:
    model: str
    max_tokens: int
    temperature: float = 0.7


@dataclass
class MessageStack:
    messages: List[Dict] = field(default_factory=list)

    @property
    def content(self):
        return self.messages

    def forget(self, n: int):
        self.messages = self.messages[:-n]

    def append(self, entry):
        self.messages.append(entry)

    def filter_on_role(self, role):
        return MessageStack([message for message in self.messages if message['role'] == role])

    def pull_text_by_role(self, role):
        for message in self.messages:
            if message['role'] == role:
                for content in message['content']:
                    if isinstance(content, TextBlock):
                        yield content.text

    def pull_tool_result(self):
        for message in self.messages:
            if message['role'] == 'user':
                for content in message['content']:
                    yield content.get('content', 'No tool result found')

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, item):
        return MessageStack(self.messages[item])


class Engine:
    """Bla bla

    """
    def __init__(self,
                 api_key_env_var: str,
                 system_prompt: str,
                 message_params: AnthropicMessageParams,
                 tools: Optional[ToolSet] = None,
                 ):
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f'Did not find an API key in environment variable {api_key_env_var}')
        self.client = Anthropic(api_key=os.getenv(api_key_env_var))
        self.system_prompt = system_prompt
        self.message_params = message_params
        if tools is None:
            self.tool_set = ToolSet()
        self.tool_set = tools
        self.tool_spec = self.tool_set.tools_spec
        self.tool_choice = None
        self.interpret_tool_use_output = True

        self._message_stack = MessageStack()

    def process(self,
                input_prompt: str,
                input_structured: Optional[Dict[str, Any]] = None,
                tool_choice_type: str = 'auto',
                tools_choice_name: Optional[str] = None,
                interpret_tool_use_output: bool = True,
                ):
        """Bla bla

        """
        self.tool_choice = {'type': tool_choice_type}
        if tools_choice_name:
            self.tool_choice['name'] = tools_choice_name
        self.interpret_tool_use_output = interpret_tool_use_output

        if input_structured:
            structured_content_str = json.dumps(input_structured)
            input_prompt += f'\n\n=== Structured input data ===\n{structured_content_str}\n=== End of structured input data ==='

        self._message_stack.append(MessageParam(
            role='user',
            content=[TextBlock(
                text=input_prompt,
                type='text',
            )]
        ))
        length_message_stack = len(self._message_stack)

        if self.what_does_ai_say():
            added_messages = self._message_stack[length_message_stack:]
            if self.interpret_tool_use_output:
                text_out = added_messages.pull_text_by_role('assistant')
            else:
                text_out = added_messages.pull_tool_result()
            return '\n\n'.join([text for text in text_out])


    def what_does_ai_say(self):
        tool_outputs = []
        response = self.client.messages.create(
            messages=self._message_stack.content,
            system=self.system_prompt,
            model=self.message_params.model,
            max_tokens=self.message_params.max_tokens,
            temperature=self.message_params.temperature,
            tools=self.tool_spec,
            tool_choice=self.tool_choice,
        )
        self._message_stack.append(MessageParam(
            role=response.role,
            content=response.content,)
        )

        for message in response.content:
            if isinstance(message, ToolUseBlock):
                tool_output = self.tool_set(message.name, **message.input)
                tool_call_id = message.id
                tool_outputs.append((tool_call_id, tool_output))

        if len(tool_outputs) > 0:
            self._message_stack.append(MessageParam(
                role='user',
                content=[
                    ToolResultBlockParam(
                        tool_use_id=tool_call_id,
                        content=tool_output,
                        type='tool_result',
                    ) for tool_call_id, tool_output in tool_outputs
                ]
            ))

        if response.stop_reason == 'tool_use':
            if self.interpret_tool_use_output:
                return self.what_does_ai_say()
            else:
                return True
        elif response.stop_reason == 'end_turn':
            return True
