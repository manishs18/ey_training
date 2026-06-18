from langchain_openai import AzureChatOpenAI

def create_plan(query, llm):

    prompt = f"""
    Break this task into executable steps.

    Query:
    {query}

    Return as numbered list.
    """

    return llm.invoke(prompt).content