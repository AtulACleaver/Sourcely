"""
Quick benchmark to measure retrieval latency at different document scales.

Two passes:
  - FAISS-only: synthetic vectors, no API calls (200 runs)
  - End-to-end: real Mistral embed + FAISS search (10 runs, costs credits)

Run from backend/:  python benchmark.py
"""

import os
import sys
import time
import statistics

import numpy as np
import faiss
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    sys.exit("MISTRAL_API_KEY not set in .env")

client = Mistral(api_key=api_key)

# chunk counts roughly mirror chunk_size=500, overlap=100 on ~1000 char/page docs
SIZES = {
    "~25 pages":  125,
    "~50 pages":  250,
    "~100 pages": 500,
    "150+ pages": 750,
}

DIM    = 1024   # mistral-embed dimension
K      = 5      # top-k retrieval
SAMPLE_QUERIES = [
    "What is the main topic of this document?",
    "Summarize the key findings.",
    "What methodology was used?",
    "Who are the authors or contributors?",
    "What conclusions were drawn?",
]


def random_vecs(n, dim):
    v = np.random.randn(n, dim).astype("float32")
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def build_index(n):
    idx = faiss.IndexFlatL2(DIM)
    idx.add(random_vecs(n, DIM))
    return idx


def embed(text):
    resp = client.embeddings.create(model="mistral-embed", inputs=[text])
    v = np.array(resp.data[0].embedding, dtype="float32")
    return v / np.linalg.norm(v)


# ── FAISS-only (no API) ───────────────────────────────────────────────────

def bench_faiss():
    print("\n⚡  FAISS search latency (synthetic embeddings, 200 runs)")
    print(f"{'Size':<14}  {'Chunks':>6}  {'Mean':>8}  {'Median':>8}  {'p95':>8}  {'p99':>8}")
    print("-" * 60)

    results = {}
    for label, n in SIZES.items():
        idx = build_index(n)
        times = []
        for _ in range(200):
            q = random_vecs(1, DIM)
            t0 = time.perf_counter()
            idx.search(q, K)
            times.append((time.perf_counter() - t0) * 1000)

        results[label] = {
            "n": n,
            "mean":   statistics.mean(times),
            "median": statistics.median(times),
            "p95":    np.percentile(times, 95),
            "p99":    np.percentile(times, 99),
        }
        r = results[label]
        print(f"{label:<14}  {n:>6}  {r['mean']:>7.2f}ms  {r['median']:>7.2f}ms  {r['p95']:>7.2f}ms  {r['p99']:>7.2f}ms")

    return results


# ── End-to-end (real API) ─────────────────────────────────────────────────

def bench_e2e():
    print("\n🌐  End-to-end latency (Mistral embed + FAISS, 10 runs)")
    print(f"{'Size':<14}  {'Chunks':>6}  {'Mean':>8}  {'Median':>8}  {'p95':>8}")
    print("-" * 55)

    results = {}
    for label, n in SIZES.items():
        idx = build_index(n)
        times = []
        for i in range(10):
            q = SAMPLE_QUERIES[i % len(SAMPLE_QUERIES)]
            t0 = time.perf_counter()
            v = embed(q)
            idx.search(v.reshape(1, -1), K)
            times.append((time.perf_counter() - t0) * 1000)

        results[label] = {
            "n": n,
            "mean":   statistics.mean(times),
            "median": statistics.median(times),
            "p95":    np.percentile(times, 95),
        }
        r = results[label]
        print(f"{label:<14}  {n:>6}  {r['mean']:>7.0f}ms  {r['median']:>7.0f}ms  {r['p95']:>7.0f}ms")
        sys.stdout.flush()

    return results


if __name__ == "__main__":
    print("Sourcely retrieval benchmark")
    print(f"k={K}  dim={DIM}  model=mistral-embed")

    faiss_results = bench_faiss()

    run_e2e = input("\nRun E2E benchmark? (makes 40 Mistral API calls) [y/N] ").strip().lower()
    if run_e2e == "y":
        bench_e2e()
    else:
        print("Skipped E2E — FAISS-only results above.")
