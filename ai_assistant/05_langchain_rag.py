from __future__ import annotations

import argparse
import json
import os
import urllib.request
from importlib import import_module

os.environ.setdefault("HF_HUB_OFFLINE", "1")

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen2.5:7b"

search = import_module("03_search").search


def retrieve_context(question: str) -> str:
    results = search(question, top_k=4)
    blocks = []
    for result in results:
        blocks.append(
            f"""[Source {result['rank']}]
File: {result['source']}
Heading: {result['heading']}
Content:
{result['text']}"""
        )
    return "\n\n".join(blocks)


def call_ollama(prompt_value) -> str:
    messages = []
    for message in prompt_value.to_messages():
        role = "user"
        if message.type == "system":
            role = "system"
        elif message.type in {"ai", "assistant"}:
            role = "assistant"
        messages.append({"role": role, "content": message.content})

    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": messages,
        "options": {"temperature": 0.1, "num_ctx": 8192},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["message"]["content"]


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are the Adbri Construction Intelligence Assistant.
Use only the retrieved context.
Answer in the same language as the question.
Give a direct conclusion, evidence, business interpretation, and citations.
Cite sources as [Source 1], [Source 2], etc.
If evidence is insufficient, say so explicitly.
Never invent numbers, dates, or table names.""",
        ),
        (
            "user",
            """Question:
{question}

Retrieved context:
{context}""",
        ),
    ]
)

# LCEL pipeline:
# question -> parallel question/context preparation -> prompt -> Ollama -> text
rag_chain = (
    {
        "question": RunnablePassthrough(),
        "context": RunnableLambda(retrieve_context),
    }
    | prompt
    | RunnableLambda(call_ollama)
    | StrOutputParser()
)


def main() -> None:
    parser = argparse.ArgumentParser(description="LangChain Adbri RAG demo.")
    parser.add_argument("question")
    args = parser.parse_args()
    print(rag_chain.invoke(args.question))


if __name__ == "__main__":
    main()
