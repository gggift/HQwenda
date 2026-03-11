from app.tools.registry import tool, get_tool_schemas, execute_tool, _TOOL_REGISTRY, _TOOL_SCHEMAS


def setup_function():
    """Clear registry before each test."""
    _TOOL_REGISTRY.clear()
    _TOOL_SCHEMAS.clear()


def test_register_tool():
    @tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "A number"},
            },
            "required": ["x"],
        },
    )
    def test_tool(x: int) -> dict:
        return {"result": x * 2}

    schemas = get_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "test_tool"
    assert schemas[0]["function"]["description"] == "A test tool"


def test_execute_tool():
    @tool(
        name="add_tool",
        description="Adds numbers",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    )
    def add_tool(a: int, b: int) -> dict:
        return {"sum": a + b}

    result = execute_tool("add_tool", '{"a": 3, "b": 5}')
    assert '"sum": 8' in result


def test_execute_unknown_tool():
    result = execute_tool("nonexistent", '{}')
    assert "error" in result
    assert "Unknown tool" in result


def test_execute_tool_with_exception():
    @tool(
        name="bad_tool",
        description="Raises error",
        parameters={"type": "object", "properties": {}},
    )
    def bad_tool() -> dict:
        raise ValueError("something broke")

    result = execute_tool("bad_tool", '{}')
    assert "error" in result
    assert "something broke" in result
