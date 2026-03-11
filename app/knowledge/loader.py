from dataclasses import dataclass
from pathlib import Path


@dataclass
class KnowledgeDoc:
    title: str
    tags: list[str]
    content: str


class KnowledgeLoader:
    def __init__(self, docs_dir: str):
        self._docs: list[KnowledgeDoc] = []
        self._load_docs(docs_dir)

    def _load_docs(self, docs_dir: str):
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            return
        for md_file in docs_path.rglob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            title, tags, body = self._parse_doc(text)
            if title or body:
                self._docs.append(KnowledgeDoc(title=title, tags=tags, content=body))

    def _parse_doc(self, content: str) -> tuple[str, list[str], str]:
        lines = content.strip().split("\n")
        title = ""
        tags = []
        body_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("# ") and not title:
                title = stripped[2:].strip()
            elif stripped.startswith("tags:"):
                tags = [t.strip() for t in stripped[5:].split(",") if t.strip()]
            elif stripped == "---":
                body_start = i + 1
                break

        body = "\n".join(lines[body_start:]).strip()
        return title, tags, body

    def search(self, keywords: list[str], max_results: int = 2) -> list[KnowledgeDoc]:
        scored = []
        for doc in self._docs:
            doc_tags_lower = [t.lower() for t in doc.tags]
            score = sum(1 for kw in keywords if kw.lower() in doc_tags_lower)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:max_results]]
