from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.3"
)

class HFProvider:

    async def generate(self, prompt):

        result = generator(
            prompt,
            max_new_tokens=300
        )

        return result[0]["generated_text"]