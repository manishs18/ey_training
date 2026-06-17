from app.services.azure_llm import AzureProvider
from app.services.claude_llm import ClaudeProvider
from app.services.hf_llm import HFProvider

azure = AzureProvider()
claude = ClaudeProvider()
hf = HFProvider()

async def route_request(prompt):

    try:
        return await azure.generate(prompt)

    except Exception:

        try:
            return await claude.generate(prompt)

        except Exception:

            return await hf.generate(prompt)