from __future__ import annotations

from typing import Any

from llm import MockVulnerableLLM


class RAGIndex:
    def __init__(self):
        self.documents: list[str] = []

    def add(self, text: str):
        self.documents.append(text)

    def query(self, question: str, mode: str = "gateway_block") -> dict[str, Any]:
        result = []
        for idx, text in enumerate(self.documents):
            if question.lower() in text.lower() or any(word in text.lower() for word in question.lower().split()):
                result.append({"id": idx, "text": text[:200]})
        llm = MockVulnerableLLM()
        answer = llm.ask(question, "\n".join(self.documents))
        return {"answer": answer, "sources": result[:4], "blocked_docs": []}
