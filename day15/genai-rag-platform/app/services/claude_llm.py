import anthropic
from app.config import settings

class ClaudeProvider:

    def __init__(self):

        self.client = anthropic.Anthropic(
            api_key=settings.CLAUDE_API_KEY
        )

    async def generate(self, prompt):

        response = self.client.messages.create(
            model="claude-sonnet-4",
            max_tokens=1000,
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        )

        return response.content[0].text