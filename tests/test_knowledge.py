import tempfile
from pathlib import Path

from app.knowledge.loader import KnowledgeLoader


def _create_test_docs(tmp_dir: str):
    ind_dir = Path(tmp_dir) / "indicators"
    ind_dir.mkdir(parents=True)
    (ind_dir / "pe.md").write_text("# 市盈率\n\ntags: PE, 市盈率, 估值\n\n---\n\nPE = 股价 / EPS")
    (ind_dir / "roe.md").write_text("# ROE\n\ntags: ROE, 净资产收益率\n\n---\n\nROE = 净利润 / 股东权益")


def test_load_docs():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)
        assert len(loader._docs) == 2


def test_search_by_keyword():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)
        results = loader.search(["PE"])
        assert len(results) == 1
        assert "市盈率" in results[0].title


def test_search_multiple_keywords():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)
        results = loader.search(["PE", "估值"])
        assert len(results) >= 1
        assert "市盈率" in results[0].title


def test_search_no_match():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)
        results = loader.search(["不存在的关键词"])
        assert len(results) == 0


def test_search_max_results():
    with tempfile.TemporaryDirectory() as tmp_dir:
        _create_test_docs(tmp_dir)
        loader = KnowledgeLoader(tmp_dir)
        results = loader.search(["ROE", "PE"], max_results=1)
        assert len(results) == 1
