import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    faithfulness,
    answer_relevancy
)

from langchain.schema import LLMResult, Generation
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        from langchain.chat_models import ChatOpenAI

import groq


def _normalize_message(message):
    role = getattr(message, "type", None) or getattr(message, "role", None) or "user"
    if role == "human":
        role = "user"
    elif role == "ai":
        role = "assistant"

    content = getattr(message, "content", "")
    if content is None:
        content = ""
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)
    else:
        content = str(content)

    data = {"role": role, "content": content}
    name = getattr(message, "name", None)
    if name:
        data["name"] = name
    return data


def _prompt_to_messages(prompt):
    messages = []
    if hasattr(prompt, "to_messages"):
        try:
            messages = prompt.to_messages() or []
        except Exception:
            messages = []

    if not messages:
        if hasattr(prompt, "to_string") and callable(prompt.to_string):
            content = prompt.to_string()
        else:
            content = str(prompt)
        return [{"role": "user", "content": content}]

    normalized = []
    for item in messages:
        if isinstance(item, list):
            normalized.extend(_normalize_message(m) for m in item)
        else:
            normalized.append(_normalize_message(item))
    return normalized


class GroqChatModel(BaseChatModel):
    def __init__(self, model: str = "compound-beta-mini", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if self.api_key is None:
            raise ValueError("GROQ_API_KEY must be set for GroqChatModel")
        self.client = groq.Groq(api_key=self.api_key)
        super().__init__()

    def _build_request(self, prompts, stop=None, **kwargs):
        messages = []
        for prompt in prompts:
            messages.extend(_prompt_to_messages(prompt))

        request = {
            "messages": messages,
            "model": self.model,
            "n": kwargs.get("n", 1),
        }
        if kwargs.get("temperature") is not None:
            request["temperature"] = kwargs.get("temperature")
        if stop is not None:
            request["stop"] = stop
        if kwargs.get("max_tokens") is not None:
            request["max_tokens"] = kwargs.get("max_tokens")
        return request

    def _build_result(self, response, n: int):
        generations = []
        for choice in list(response.choices)[:n]:
            message = getattr(choice, "message", None)
            if message is None:
                text = ""
            else:
                text = getattr(message, "content", "")
                if isinstance(text, list):
                    text = " ".join(str(item) for item in text)
                else:
                    text = str(text)
            generations.append(Generation(text=text))
        return LLMResult(generations=[generations], llm_output=response.dict())

    def generate_prompt(self, prompts, stop=None, callbacks=None, **kwargs):
        request = self._build_request(prompts, stop=stop, **kwargs)
        response = self.client.chat.completions.create(**request)
        return self._build_result(response, n=request["n"])

    async def agenerate_prompt(self, prompts, stop=None, callbacks=None, **kwargs):
        return self.generate_prompt(prompts, stop=stop, callbacks=callbacks, **kwargs)


def _create_llm():
    provider = os.getenv("RAGAS_LLM_PROVIDER", "").strip().lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if provider == "openai":
        if not openai_key:
            raise ValueError("RAGAS_LLM_PROVIDER=openai but OPENAI_API_KEY is not set")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=openai_key,
        )

    if provider == "groq":
        if not groq_key:
            raise ValueError("RAGAS_LLM_PROVIDER=groq but GROQ_API_KEY is not set")
        return GroqChatModel(
            model=os.getenv("GROQ_MODEL", "compound-beta-mini"),
            api_key=groq_key,
        )

    if groq_key:
        return GroqChatModel(
            model=os.getenv("GROQ_MODEL", "compound-beta-mini"),
            api_key=groq_key,
        )

    if openai_key:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=openai_key,
        )

    return None


def run_ragas(df):
    if isinstance(df["contexts"].iloc[0], str):
        df = df.copy()
        df["contexts"] = df["contexts"].apply(lambda x: [x] if isinstance(x, str) else x)

    dataset = Dataset.from_pandas(df)
    llm = _create_llm()

    if llm is None:
        raise EnvironmentError(
            "No RAGAS LLM key found. Set OPENAI_API_KEY or GROQ_API_KEY."
        )

    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
        ],
        llm=llm,
    )

    return result.to_pandas()