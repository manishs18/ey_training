# search_evaluation.py

import math

# -----------------------------
# Ground Truth Dataset
# -----------------------------
ground_truth = {
    "azure service bus": {
        "relevant_docs": ["doc1", "doc3"]
    },
    "python asyncio queue": {
        "relevant_docs": ["doc5"]
    },
    "gan architecture": {
        "relevant_docs": ["doc7", "doc8"]
    }
}

# -----------------------------
# Search Engine Results
# -----------------------------
search_results = {
    "azure service bus": ["doc2", "doc3", "doc1"],
    "python asyncio queue": ["doc5", "doc9"],
    "gan architecture": ["doc8", "doc10", "doc7"]
}

# -----------------------------
# MRR IMPLEMENTATION
# -----------------------------
def reciprocal_rank(results, relevant_docs):
    for rank, doc in enumerate(results, start=1):
        if doc in relevant_docs:
            return 1 / rank
    return 0


def mean_reciprocal_rank(ground_truth, search_results):
    scores = []

    for query, data in ground_truth.items():
        rr = reciprocal_rank(
            search_results.get(query, []),
            data["relevant_docs"]
        )
        scores.append(rr)

    return sum(scores) / len(scores)


# -----------------------------
# DCG & NDCG IMPLEMENTATION
# -----------------------------
def dcg(relevances):
    score = 0.0
    for i, rel in enumerate(relevances, start=1):
        score += rel / math.log2(i + 1)
    return score


def ndcg(relevances):
    actual = dcg(relevances)
    ideal = dcg(sorted(relevances, reverse=True))

    if ideal == 0:
        return 0.0

    return actual / ideal


# -----------------------------
# FULL EVALUATION PIPELINE
# -----------------------------
def evaluate():
    print("=== SEARCH EVALUATION ===\n")

    # ---- MRR ----
    mrr = mean_reciprocal_rank(ground_truth, search_results)
    print(f"MRR: {mrr:.4f}")

    # ---- NDCG ----
    ndcg_scores = []

    for query, data in ground_truth.items():
        results = search_results.get(query, [])

        relevances = []
        for doc in results:
            if doc in data["relevant_docs"]:
                relevances.append(1)
            else:
                relevances.append(0)

        ndcg_scores.append(ndcg(relevances))

    avg_ndcg = sum(ndcg_scores) / len(ndcg_scores)
    print(f"NDCG: {avg_ndcg:.4f}")


# -----------------------------
# RUN SCRIPT
# -----------------------------
if __name__ == "__main__":
    evaluate()