import faiss
import numpy as np
import os
import pickle
import datetime
from sentence_transformers import SentenceTransformer

class MemoryModel:
    def __init__(self, index_file="elda_memory.index", store_file="elda_store.pkl"):
        self.index_file = index_file
        self.store_file = store_file
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        self.dimension = 384
        
        # Load or Create Index
        if os.path.exists(self.index_file) and os.path.exists(self.store_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.store_file, "rb") as f:
                self.documents = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
    
    def add_memory(self, text, metadata=None):
        # 1. Vector Store (For AI Recall)
        vector = self.encoder.encode([text])
        self.index.add(np.array(vector, dtype=np.float32))
        self.documents.append({"text": text, "metadata": metadata})
        self.save()
        
        # 2. Text File Backup (For "Saving everything on a thing" - human readable)
        try:
            with open("conversation_history.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {text}\n")
        except Exception as e:
            print(f"Log Error: {e}")
        
    def reset(self):
        """Clears the FAISS memory stores intentionally."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        if os.path.exists(self.index_file):
            os.remove(self.index_file)
        if os.path.exists(self.store_file):
            os.remove(self.store_file)

    def retrieve_relevant(self, query, k=3):
        if self.index.ntotal == 0:
            return []
            
        # Contextual filter: only fetch past memory if user actually asks about the past
        # This stops the model from getting confused with old memories on general questions.
        past_keywords = [
            "remember", "past", "told", "earlier", "yesterday", 
            "last time", "before", "did i", "was i", "said", 
            "already", "have i", "who", "what", "where",
            "forget", "forgot", "remind", "history", "again"
        ]
        
        query_lower = query.lower()
        if not any(kw in query_lower for kw in past_keywords):
            return []
            
        vector = self.encoder.encode([query])
        distances, indices = self.index.search(np.array(vector, dtype=np.float32), k)
        
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.documents):
                results.append(self.documents[i]['text'])
        return results

    def save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.store_file, "wb") as f:
            pickle.dump(self.documents, f)
