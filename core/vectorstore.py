import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma")


class VectorStore:
    def __init__(self):
        os.makedirs(CHROMA_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        try:
            self.collection = self.client.get_collection("rag_docs")
        except Exception:
            self.collection = None

    def add(self, chunks, source_name):
        if self.collection is None:
            self.collection = self.client.get_or_create_collection("rag_docs")
        embeddings = self.model.encode(chunks).tolist()
        offset = self.collection.count()
        ids = [f"{source_name}_{i + offset}" for i in range(len(chunks))]
        metadatas = [{"source": source_name}] * len(chunks)
        self.collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)

    def query(self, q, n=5):
        if not self.collection:
            return [], []
        vec = self.model.encode(q).tolist()
        results = self.collection.query(query_embeddings=[vec], n_results=n)
        return results["documents"][0], results["metadatas"][0]

    def remove(self, source_name):
        if self.collection:
            self.collection.delete(where={"source": source_name})

    def count(self):
        return self.collection.count() if self.collection else 0

    def clear(self):
        try:
            self.client.delete_collection("rag_docs")
        except Exception:
            pass
        self.collection = None
