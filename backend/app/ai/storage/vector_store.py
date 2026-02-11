import chromadb
import os
import logging

logger = logging.getLogger(__name__)


class VectorStore:

    def __init__(self, path="./chroma_db", collection_name="cvs"):
        self.path = path
        self.collection_name = collection_name

        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)

        # Use PersistentClient for data to survive restarts
        self.client = chromadb.PersistentClient(path=path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def clear(self):
        """
        Clear all data from the collection by deleting and recreating it.
        Required when changing embedding models (dimension changes).
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        logger.info(f"Created fresh collection '{self.collection_name}'")

    def add(self, ids, documents, embeddings, metadatas):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        # Persistence is automatic when `persist_directory` is set

    def search(self, query_embedding, n_results=10, where=None):

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
