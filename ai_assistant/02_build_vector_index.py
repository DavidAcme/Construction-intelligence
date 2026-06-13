from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


AI_DIR = Path(__file__).resolve().parent
CHUNKS_FILE = AI_DIR / "data" / "chunks.json"
INDEX_FILE = AI_DIR / "data" / "adbri_knowledge.faiss"
METADATA_FILE = AI_DIR / "data" / "index_metadata.json"

# Multilingual model because the knowledge base contains English and Chinese.
MODEL_NAME = "intfloat/multilingual-e5-small"


def main() -> None:
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    if not chunks:
        raise RuntimeError("No chunks found. Run 01_prepare_documents.py first.")

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, local_files_only=True)

    # E5 models expect passage/query prefixes for retrieval.
    passages = [f"passage: {chunk['text']}" for chunk in chunks]
    embeddings = model.encode(
        passages,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)

    # Normalised vectors + inner product = cosine similarity.
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    METADATA_FILE.write_text(
        json.dumps(
            {
                "model_name": MODEL_NAME,
                "embedding_dimension": int(embeddings.shape[1]),
                "chunk_count": len(chunks),
                "chunks": chunks,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Chunks indexed: {index.ntotal}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"FAISS index: {INDEX_FILE}")
    print(f"Metadata: {METADATA_FILE}")


if __name__ == "__main__":
    main()
