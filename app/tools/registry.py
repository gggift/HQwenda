import json
from typing import Callable

_TOOL_REGISTRY: dict[str, Callable] = {}
_TOOL_SCHEMAS: list[dict] = []


def tool(name: str, description: str, parameters: dict):
    """Decorator to register a function as an agent tool."""

    def decorator(func: Callable):
        _TOOL_REGISTRY[name] = func
        _TOOL_SCHEMAS.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            }
        )
        return func

    return decorator


def get_tool_schemas() -> list[dict]:
    """Return all registered tool schemas for LLM function calling."""
    return _TOOL_SCHEMAS


def execute_tool(name: str, arguments: str) -> str:
    """Execute a registered tool by name with JSON arguments string."""
    func = _TOOL_REGISTRY.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
    try:
        args = json.loads(arguments)
        result = func(**args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
