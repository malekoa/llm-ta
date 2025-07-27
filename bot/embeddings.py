from openai import OpenAI
from bot.config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def embed_chunk(text: str) -> list[float]:
    """
    Generate an embedding vector for a given text chunk.
    """
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding