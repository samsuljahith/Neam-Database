import os
from storage.vector_store import VectorStore
from config import settings

class PersistenceManager:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.data_dir = settings.data_dir

    def load_all(self):
        if not os.path.exists(self.data_dir): return
        for f in os.listdir(self.data_dir):
            if f.endswith(".index"):
                name = f.replace(".index", "")
                self.vector_store.load(name)
                print(f"Loaded: {name}")

    def save_all(self):
        for name in self.vector_store.indexes:
            self.vector_store.save(name)
            print(f"Saved: {name}")
