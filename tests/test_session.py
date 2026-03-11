from app.session.manager import SessionManager


def test_create_session():
    sm = SessionManager()
    sid = sm.create_session()
    assert isinstance(sid, str)
    assert len(sid) > 0


def test_add_and_get_history():
    sm = SessionManager()
    sid = sm.create_session()
    sm.add_message(sid, "user", "hello")
    sm.add_message(sid, "assistant", "hi")
    history = sm.get_history(sid)
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "hello"}
    assert history[1] == {"role": "assistant", "content": "hi"}


def test_history_truncation():
    sm = SessionManager(max_rounds=2)
    sid = sm.create_session()
    # Add 3 rounds (6 messages), should keep only last 2 rounds (4 messages)
    for i in range(3):
        sm.add_message(sid, "user", f"q{i}")
        sm.add_message(sid, "assistant", f"a{i}")
    history = sm.get_history(sid)
    assert len(history) == 4
    assert history[0]["content"] == "q1"


def test_delete_session():
    sm = SessionManager()
    sid = sm.create_session()
    sm.add_message(sid, "user", "test")
    sm.delete_session(sid)
    history = sm.get_history(sid)
    assert history == []


def test_get_history_nonexistent():
    sm = SessionManager()
    history = sm.get_history("nonexistent")
    assert history == []
