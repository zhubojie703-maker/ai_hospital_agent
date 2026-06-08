from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RetrievedDoc:
    title: str
    path: str
    score: int
    content: str


class HospitalKnowledgeBase:
    def __init__(self, docs_dir: str | Path = "hospital_docs"):
        self.docs_dir = Path(docs_dir)
        self.documents = self._load_documents()

    def _load_documents(self) -> list[RetrievedDoc]:
        docs: list[RetrievedDoc] = []
        if not self.docs_dir.exists():
            return docs
        for path in sorted(self.docs_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = path.stem
            docs.append(RetrievedDoc(title=title, path=str(path), score=0, content=text))
        return docs

    @staticmethod
    def _keywords(text: str) -> set[str]:
        words = set(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", text))
        extra_terms = {
            term
            for term in ("药占比", "床位使用率", "平均住院日", "医保控费", "绩效考核", "手术分级")
            if term in text
        }
        return words.union(extra_terms)

    def retrieve(self, question: str, top_k: int = 3) -> list[RetrievedDoc]:
        query_terms = self._keywords(question)
        ranked: list[RetrievedDoc] = []
        for doc in self.documents:
            doc_terms = self._keywords(doc.title + "\n" + doc.content)
            score = len(query_terms.intersection(doc_terms))
            if score > 0:
                ranked.append(
                    RetrievedDoc(title=doc.title, path=doc.path, score=score, content=doc.content)
                )
        return sorted(ranked, key=lambda item: item.score, reverse=True)[:top_k]

    def answer(self, question: str) -> dict:
        docs = self.retrieve(question)
        if not docs:
            return {
                "answer": "当前知识库未找到依据。建议补充医院制度、指标口径或政策文档后再查询。",
                "sources": [],
            }

        snippets = []
        for doc in docs:
            clean = re.sub(r"\s+", " ", doc.content).strip()
            snippets.append(f"【{doc.title}】{clean[:420]}")

        answer = "根据当前医院知识库：\n\n" + "\n\n".join(snippets)
        answer += "\n\n注意：以上为管理口径说明，不构成诊疗建议。"
        return {
            "answer": answer,
            "sources": [{"title": doc.title, "path": doc.path, "score": doc.score} for doc in docs],
        }
