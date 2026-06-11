from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SemanticComparator:

    def __init__(self):

        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def compare(self, old_chunks, new_chunks):

        old_embeddings = self.embedding_model.embed_documents(
            old_chunks
        )

        new_embeddings = self.embedding_model.embed_documents(
            new_chunks
        )

        results = []

        for idx, new_chunk in enumerate(new_chunks):

            scores = cosine_similarity(
                [new_embeddings[idx]],
                old_embeddings
            )[0]

            best_index = np.argmax(scores)

            results.append(
                {
                    "new_chunk": new_chunk,
                    "old_chunk": old_chunks[best_index],
                    "similarity": float(scores[best_index])
                }
            )

        return results