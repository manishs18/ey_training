def generate_query_insight(row):

    insight = f"""
    Query {row['query_id']} took
    {row['latency_ms']} ms.

    Context Precision:
    {row['context_precision']:.2f}

    Faithfulness:
    {row['faithfulness']:.2f}

    Answer Relevance:
    {row['answer_relevancy']:.2f}
    """

    return insight

# df["insight"] = df.apply(
#     generate_query_insight,
#     axis=1
# )