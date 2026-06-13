from __future__ import annotations

import argparse
import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


AI_DIR = Path(__file__).resolve().parent
INDEX_FILE = AI_DIR / "data" / "adbri_knowledge.faiss"
METADATA_FILE = AI_DIR / "data" / "index_metadata.json"


def search(question: str, top_k: int = 5) -> list[dict[str, object]]:
    metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    chunks = metadata["chunks"]
    # The model was downloaded when the index was built. Force offline loading
    # so every search does not contact Hugging Face for a version check.
    model = SentenceTransformer(
        metadata["model_name"],
        local_files_only=True,
    )
    index = faiss.read_index(str(INDEX_FILE))

    query_vector = model.encode(
        [f"query: {question}"],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    scores, indexes = index.search(query_vector, top_k)

    results = []
    for rank, (score, chunk_index) in enumerate(
        zip(scores[0], indexes[0]), start=1
    ):
        chunk = chunks[int(chunk_index)]
        results.append(
            {
                "rank": rank,
                "score": float(score),
                "source": chunk["source"],
                "heading": chunk["heading"],
                "text": chunk["text"],
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the Adbri knowledge base.")
    parser.add_argument("question", help="Question in English or Chinese.")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    print(f"\nQuestion: {args.question}\n")
    for result in search(args.question, args.top_k):
        print("=" * 80)
        print(f"Rank: {result['rank']} | Similarity: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Heading: {result['heading']}")
        print("-" * 80)
        print(result["text"][:1_000])
        print()


if __name__ == "__main__":
    main()
