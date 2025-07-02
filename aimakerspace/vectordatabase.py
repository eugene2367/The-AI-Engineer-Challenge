import numpy as np
from typing import List, Tuple, Callable, Optional, Union, Dict
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Computes the cosine similarity between two vectors."""
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


class VectorDatabase:
    def __init__(self):
        self.vectors: Dict[str, np.ndarray] = {}  # key: str, value: np.ndarray
        # No embedding_model at construction

    def insert(self, key: str, vector: np.ndarray) -> None:
        self.vectors[key] = vector

    def search(
        self,
        query_vector: np.ndarray,
        k: int,
        distance_measure: Callable = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        scores = [
            (key, distance_measure(query_vector, vector))
            for key, vector in self.vectors.items()
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
        api_key: Optional[str] = None,
    ) -> Union[List[Tuple[str, float]], List[str]]:
        embedding_model = EmbeddingModel()
        query_vector = np.array(embedding_model.get_embedding(query_text, api_key=api_key))
        results = self.search(query_vector, k, distance_measure)
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> Optional[np.ndarray]:
        # Returns None if key is missing
        return self.vectors.get(key, None)

    async def abuild_from_list(self, list_of_text: List[str], api_key: Optional[str] = None) -> "VectorDatabase":
        embedding_model = EmbeddingModel()
        embeddings = await embedding_model.async_get_embeddings(list_of_text, api_key=api_key)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, np.array(embedding))
        return self


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2

    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
