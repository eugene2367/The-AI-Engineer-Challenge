from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
import openai
from typing import List, Optional
import os
import asyncio


class EmbeddingModel:
    def __init__(self, embeddings_model_name: str = "text-embedding-3-small"):
        load_dotenv()
        self.embeddings_model_name = embeddings_model_name

    def _get_api_key(self, api_key: Optional[str] = None) -> str:
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set. Pass it as an argument or set it in the environment.")
        return key

    def _get_async_client(self, api_key: Optional[str] = None):
        return AsyncOpenAI(api_key=self._get_api_key(api_key))

    def _get_client(self, api_key: Optional[str] = None):
        return OpenAI(api_key=self._get_api_key(api_key))

    async def async_get_embeddings(self, list_of_text: List[str], api_key: Optional[str] = None) -> List[List[float]]:
        async_client = self._get_async_client(api_key)
        embedding_response = await async_client.embeddings.create(
            input=list_of_text, model=self.embeddings_model_name
        )
        return [embeddings.embedding for embeddings in embedding_response.data]

    async def async_get_embedding(self, text: str, api_key: Optional[str] = None) -> List[float]:
        async_client = self._get_async_client(api_key)
        embedding = await async_client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )
        return embedding.data[0].embedding

    def get_embeddings(self, list_of_text: List[str], api_key: Optional[str] = None) -> List[List[float]]:
        client = self._get_client(api_key)
        embedding_response = client.embeddings.create(
            input=list_of_text, model=self.embeddings_model_name
        )
        return [embeddings.embedding for embeddings in embedding_response.data]

    def get_embedding(self, text: str, api_key: Optional[str] = None) -> List[float]:
        client = self._get_client(api_key)
        embedding = client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )
        return embedding.data[0].embedding


if __name__ == "__main__":
    embedding_model = EmbeddingModel()
    print(asyncio.run(embedding_model.async_get_embedding("Hello, world!")))
    print(
        asyncio.run(
            embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
        )
    )
