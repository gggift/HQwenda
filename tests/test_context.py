from app.session.manager import SessionManager
from app.knowledge.loader import KnowledgeLoader
import tempfile
from pathlib import Path


def _make_loader_with_docs():
    tmp = tempfile.mkdtemp()
    ind_dir = Path(tmp) / "indicators"
    ind_dir.mkdir()
    (ind_dir / "pe.md").write_text("# PE\n\ntags: PE, 市盈率\n\n---\n\nPE解释内容")
    return KnowledgeLoader(tmp), tmp


def test_assemble_context_basic():
    sm = SessionManager()
    sid = sm.create_session()
    loader, _ = _make_loader_with_docs()

    from app.agent.context import assemble_context

    system_prompt, messages = assemble_context(
        "平安银行今天怎么样", sid, sm, loader
    )
    assert "金融数据分析助手" in system_prompt
    assert messages[-1]["content"] == "平安银行今天怎么样"


def test_assemble_context_with_knowledge():
    sm = SessionManager()
    sid = sm.create_session()
    loader, _ = _make_loader_with_docs()

    from app.agent.context import assemble_context

    # "PE" keyword should trigger knowledge doc inclusion
    system_prompt, messages = assemble_context(
        "什么是PE？", sid, sm, loader
    )
    assert "PE解释内容" in system_prompt


def test_assemble_context_with_history():
    sm = SessionManager()
    sid = sm.create_session()
    sm.add_message(sid, "user", "你好")
    sm.add_message(sid, "assistant", "你好！")
    loader, _ = _make_loader_with_docs()

    from app.agent.context import assemble_context

    system_prompt, messages = assemble_context(
        "今天天气怎么样", sid, sm, loader
    )
    assert len(messages) == 3  # 2 history + 1 new
    assert messages[0]["content"] == "你好"
