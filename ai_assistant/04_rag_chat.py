from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request

# Prevent Hugging Face version checks. The embedding model is cached locally.
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from importlib import import_module


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:7b"


def load_search_function():
    # The file starts with a number, so import it dynamically.
    module = import_module("03_search")
    return module.search


def build_context(results: list[dict[str, object]]) -> str:
    sections = []
    for result in results:
        sections.append(
            "\n".join(
                [
                    f"[Source {result['rank']}]",
                    f"File: {result['source']}",
                    f"Heading: {result['heading']}",
                    f"Similarity: {result['score']:.4f}",
                    "Content:",
                    str(result["text"]),
                ]
            )
        )
    return "\n\n".join(sections)


def ask_ollama(question: str, context: str, model: str) -> str:
    system_prompt = """
You are the Adbri Construction Intelligence Assistant.

Answer only from the supplied retrieved context.

Rules:
1. Answer in the same language as the user's question.
2. Start with a direct conclusion.
3. Then provide evidence and business interpretation.
4. Cite evidence using [Source 1], [Source 2], etc.
5. Do not invent numbers, dates, table names, or conclusions.
6. If the context is insufficient, explicitly say that the available evidence
   is insufficient and identify what information is missing.
7. Distinguish factual evidence from your business interpretation.
8. Keep the answer concise but analytically useful.
""".strip()

    user_prompt = f"""
Question:
{question}

Retrieved context:
{context}

Produce:
- Conclusion
- Evidence
- Business interpretation
- Sources
""".strip()

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": 0.1,
            "num_ctx": 8192,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Confirm that the Ollama application "
            "is running at http://127.0.0.1:11434."
        ) from exc

    return result["message"]["content"].strip()


def answer_question(
    question: str,
    model: str = DEFAULT_MODEL,
    top_k: int = 4,
) -> tuple[str, list[dict[str, object]]]:
    search = load_search_function()
    results = search(question, top_k=top_k)
    context = build_context(results)
    answer = ask_ollama(question, context, model)
    return answer, results


def print_sources(results: list[dict[str, object]]) -> None:
    print("\nRetrieved sources:")
    for result in results:
        print(
            f"[Source {result['rank']}] {result['source']} | "
            f"{result['heading']} | score={result['score']:.4f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask the local Adbri RAG assistant."
    )
    parser.add_argument("question", nargs="?", help="Question to ask.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--top-k", type=int, default=4)
    args = parser.parse_args()

    if args.question:
        answer, results = answer_question(args.question, args.model, args.top_k)
        print("\nAnswer:\n")
        print(answer)
        print_sources(results)
        return

    print(f"Adbri RAG Assistant ({args.model})")
    print("Type exit to stop.\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        answer, results = answer_question(question, args.model, args.top_k)
        print("\nAnswer:\n")
        print(answer)
        print_sources(results)
        print()


if __name__ == "__main__":
    main()
