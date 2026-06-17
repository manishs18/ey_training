from app.services.embeddings import create_embedding
from app.services.llm_router import route_request

async def answer_question(question):

    query_vector = create_embedding(question)

    context = "Retrieved context from vector DB"

    prompt = f"""
    Context:
    {context}

    Question:
    {question}
    """

    response = await route_request(prompt)

    return response