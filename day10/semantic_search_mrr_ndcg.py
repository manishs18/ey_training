# semantic_search_evaluation.py

import math
import numpy as np
from sentence_transformers import SentenceTransformer

# ==========================================
# DOCUMENT CORPUS
# ==========================================

documents = {
    "doc1": "Azure Service Bus supports enterprise messaging and queues.",
    "doc2": "Python asyncio queue enables asynchronous communication.",
    "doc3": "Azure topics and subscriptions allow pub-sub messaging.",
    "doc4": "Deep learning uses neural networks for prediction.",
    "doc5": "GANs generate realistic images using adversarial training.",
}

# ==========================================
# GROUND TRUTH
# ==========================================

ground_truth = {
    "azure messaging": ["doc1", "doc3"],
    "python async queue": ["doc2"],
    "gan architecture": ["doc5"],
}

# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==========================================
# EMBED DOCUMENTS
# ==========================================

doc_ids = list(documents.keys())
doc_texts = list(documents.values())

print("Generating document embeddings...")
doc_embeddings = model.encode(
    doc_texts,
    convert_to_numpy=True,
    normalize_embeddings=True
)

# ==========================================
# COSINE SIMILARITY SEARCH
# ==========================================

def semantic_search(query, top_k=5):
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores = np.dot(doc_embeddings, query_embedding)

    ranked_idx = np.argsort(scores)[::-1]

    results = []

    for idx in ranked_idx[:top_k]:
        results.append(
            (
                doc_ids[idx],
                documents[doc_ids[idx]],
                float(scores[idx])
            )
        )

    return results

# ==========================================
# MRR
# ==========================================

def reciprocal_rank(results, relevant_docs):

    for rank, doc in enumerate(results, start=1):
        if doc in relevant_docs:
            return 1.0 / rank

    return 0.0


def compute_mrr():

    rr_scores = []

    for query, relevant_docs in ground_truth.items():

        retrieved = semantic_search(query)

        ranked_docs = [r[0] for r in retrieved]

        rr = reciprocal_rank(
            ranked_docs,
            relevant_docs
        )

        rr_scores.append(rr)

    return sum(rr_scores) / len(rr_scores)

# ==========================================
# NDCG
# ==========================================

def dcg(relevances):

    score = 0.0

    for i, rel in enumerate(relevances, start=1):
        score += rel / math.log2(i + 1)

    return score


def ndcg(relevances):

    actual_dcg = dcg(relevances)

    ideal_dcg = dcg(
        sorted(relevances, reverse=True)
    )

    if ideal_dcg == 0:
        return 0

    return actual_dcg / ideal_dcg


def compute_ndcg():

    scores = []

    for query, relevant_docs in ground_truth.items():

        retrieved = semantic_search(query)

        ranked_docs = [r[0] for r in retrieved]

        relevances = []

        for doc in ranked_docs:
            relevances.append(
                1 if doc in relevant_docs else 0
            )

        scores.append(ndcg(relevances))

    return sum(scores) / len(scores)

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print("\n=== SAMPLE SEARCHES ===")

    sample_queries = [
        "azure messaging",
        "python async queue",
        "gan architecture"
    ]

    for query in sample_queries:

        print(f"\nQuery: {query}")

        results = semantic_search(query)

        for rank, (doc_id, text, score) in enumerate(results, start=1):

            print(
                f"{rank}. {doc_id} "
                f"(score={score:.4f})"
            )
            print(f"   {text}")

    print("\n=== EVALUATION ===")

    mrr = compute_mrr()
    avg_ndcg = compute_ndcg()

    print(f"MRR       : {mrr:.4f}")
    print(f"Avg NDCG  : {avg_ndcg:.4f}")