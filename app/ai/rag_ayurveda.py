import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

class AyurvedaKnowledgeBase:
    def __init__(self, index_file="ayurveda.index", store_file="ayurveda_store.pkl"):
        self.index_file = index_file
        self.store_file = store_file
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        self.dimension = 384
        
        if os.path.exists(self.index_file) and os.path.exists(self.store_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.store_file, "rb") as f:
                self.documents = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.seed_knowledge() # Load initial data
    
    def seed_knowledge(self):
        # Basic Ayurveda concepts relevant to elderly care
        knowledge = [
            "Brahmi (Bacopa monnieri) is traditionally used to enhance memory and cognitive function.",
            "Ashwagandha (Withania somnifera) helps reduce stress and supports nervous system health in the elderly.",
            "Turmeric (Curcuma longa) has anti-inflammatory properties and may support brain health.",
            "Establish a daily routine (Dinacharya) to reduce confusion and anxiety in dementia patients.",
            "Warm oil massage (Abhyanga) with sesame oil can calm Vata dosha and improve sleep.",
            "Medicated ghee (Ghrita) is often recommended for nourishing the brain tissues.",
            "Keep the environment calm and avoid loud noises to prevent aggravating Vata.",
            "Light, warm, and cooked foods are easier to digest for seniors and support Ojas.",
            "Shankhpushpi is another herb valued for its intellect-promoting (Medhya) properties."
        ]
        print("Seeding Ayurveda Knowledge...")
        for k in knowledge:
            self.add_document(k)
        print("Ayurveda Knowledge Seeded.")

    def add_document(self, text):
        vector = self.encoder.encode([text])
        self.index.add(np.array(vector, dtype=np.float32))
        self.documents.append(text)
        self.save()
        
    def retrieve(self, query, k=2):
        if self.index.ntotal == 0:
            return []
            
        vector = self.encoder.encode([query])
        distances, indices = self.index.search(np.array(vector, dtype=np.float32), k)
        
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.documents):
                results.append(self.documents[i])
        return results

    def save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.store_file, "wb") as f:
            pickle.dump(self.documents, f)