from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@patch("app.api.chat.run_agent", return_value="测试回答")
@patch("app.api.chat.assemble_context", return_value=("system", [{"role": "user", "content": "test"}]))
def test_chat_endpoint(mock_ctx, mock_agent):
    from app.main import app

    client = TestClient(app)

    # Create session first
    resp = client.post("/api/session/new")
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # Send message
    resp = client.post(
        "/api/chat",
        json={"session_id": session_id, "message": "你好"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "测试回答"
    assert data["session_id"] == session_id


def test_new_session():
    from app.main import app

    client = TestClient(app)
    resp = client.post("/api/session/new")
    assert resp.status_code == 200
    assert "session_id" in resp.json()


def test_delete_session():
    from app.main import app

    client = TestClient(app)

    resp = client.post("/api/session/new")
    session_id = resp.json()["session_id"]

    resp = client.delete(f"/api/session/{session_id}")
    assert resp.status_code == 200
