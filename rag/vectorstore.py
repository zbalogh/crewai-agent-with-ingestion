import chromadb
from rag.embeddings import LocalEmbedding

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chromadb")
        self.collection = self.client.get_or_create_collection("data")
        self.embedder = LocalEmbedding()

    def add_documents(self, texts, metadatas, ids):
        embeddings = self.embedder.embed(texts)
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )

    def search(self, query, k=3):
        query_embedding = self.embedder.embed([query])[0]
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )
