"""Bla bla

"""
from typing import Sequence, Dict, Optional, Any, List
import json


class ToolSet:
    def __init__(self,
                 tool_spec_file: Optional[str] = None,
                 tools_to_include: Optional[Sequence[str]] = None,
                 ):
        if tool_spec_file is None:
            self._tools = []
        else:
            with open(tool_spec_file, 'r') as f:
                self._tools = json.load(f)
        if tools_to_include is not None:
            self._tools = [tool for tool in self._tools if tool['name'] in tools_to_include]

    def __call__(self, tool_name: str, **kwargs) -> str:
        try:
            _tool_exec = getattr(self, tool_name)
        except AttributeError:
            raise ValueError(f'Unknown tool name {tool_name}')
        return _tool_exec(**kwargs)

    @property
    def tools_spec(self) -> List[Dict[str, Any]]:
        return self._tools
