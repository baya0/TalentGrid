from app.ai.ingestion.chunker import CVChunker
from app.ai.ingestion.embedder import Embedder
from app.ai.storage.vector_store import VectorStore


def clean_metadata(meta):
    # استبدل None بقيم فارغة مناسبة
    if isinstance(meta, dict):
        return {k: ("" if v is None else v) for k, v in meta.items()}
    return meta


class IngestionPipeline:

    def __init__(self):

        self.chunker = CVChunker()
        self.embedder = Embedder()
        self.store = VectorStore()

    def ingest_one(self, cv_json: dict):
        """
        إدخال CV واحد
        """

        chunks = self.chunker.chunk(cv_json)

        for chunk in chunks:

            vector = self.embedder.embed(chunk["text"])
            metadata_clean = clean_metadata(chunk["metadata"])

            self.store.add(
                ids=[chunk["id"]],
                documents=[chunk["text"]],
                embeddings=[vector],
                metadatas=[metadata_clean],
            )

    def ingest_many(self, cvs: list[dict]):
        """
        إدخال عدة CVs دفعة واحدة
        """

        for cv in cvs:
            self.ingest_one(cv)
