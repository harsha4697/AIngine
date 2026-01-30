from sentence_transformers import SentenceTransformer
import time

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model = None
        return cls._instance

    def initialize(self):
        """
        Loads the tiny embedding model into System RAM (CPU).
        """
        print("🧠 Loading Embedding Model (CPU)...")
        start = time.time()
        # all-MiniLM-L6-v2 creates 384-dimensional vectors
        # It is optimized for semantic search
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        print(f"✅ Embedding Model loaded in {time.time() - start:.2f}s")

    def embed_text(self, text: str):
        """
        Converts text -> Vector[384]
        """
        if not self.model:
            self.initialize()
        
        # encode returns a numpy array, we convert to list for database storage
        embedding = self.model.encode(text)
        return embedding.tolist()

# Global instance
embedding_service = EmbeddingService()