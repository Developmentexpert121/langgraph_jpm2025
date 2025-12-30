import pickle
from typing import List, Dict
import numpy as np
from tiktoken import encoding_for_model
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_chunks(pickle_path: str = "data/processed/semantic_chunks.pkl") -> List[Dict]:
    with open(pickle_path, "rb") as f:
        return pickle.load(f)

def build_search_text(chunk: Dict) -> str:
    parts = []
    if chunk.get("heading"):
        parts.append(chunk["heading"])
    if chunk.get("subheading"):
        parts.append(chunk["subheading"])
    if chunk.get("text"):
        parts.append(chunk["text"])
    for img in chunk.get("images", []):
        if img.get("ocr_text"):
            parts.append(img["ocr_text"])
    return " ".join(parts)

def embed_text(text: str) -> List[float]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding


def build_chunk_embeddings(chunks: List[Dict]) -> None:
    for c in chunks:
        if "embedding" not in c:
            c["embedding"] = embed_text(build_search_text(c))

def semantic_search(chunks: List[Dict], query: str, top_k: int = 5) -> List[Dict]:
    query_emb = np.array(embed_text(query))
    scored_chunks = []

    for c in chunks:
        chunk_emb = np.array(c["embedding"])
        sim = np.dot(query_emb, chunk_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb) + 1e-8
        )
        scored_chunks.append((sim, c))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored_chunks[:top_k]]

if __name__ == "__main__":
    chunks = load_chunks()
    build_chunk_embeddings(chunks)

    query = "AI equities Apple Microsoft valuation risk"
    top_chunks = semantic_search(chunks, query, top_k=5)

    for c in top_chunks:
        print(f"[{c['doc_name']} | {c.get('heading', 'N/A')} | Pages {c.get('page_start','?')}-{c.get('page_end','?')}]")
        print(c["text"][:300], "...\n")
