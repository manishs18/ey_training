def count_tokens(text):
    return len(text.split())

def process_tokens(df):

    context_tokens = []

    for contexts in df["contexts"]:

        joined = " ".join(contexts)

        context_tokens.append(
            count_tokens(joined)
        )

    df["context_tokens"] = context_tokens

    df["answer_tokens"] = df["answer"].apply(
        count_tokens
    )

    df["total_tokens"] = (
        df["context_tokens"]
        + df["answer_tokens"]
    )

    return df