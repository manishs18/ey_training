def validate(query, result, llm):

    prompt = f"""
    Query:
    {query}

    Result:
    {result}

    Is result correct?

    Return:
    PASS or FAIL
    """

    return llm.invoke(prompt).content