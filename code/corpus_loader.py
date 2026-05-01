import os
import json
from typing import Dict, List, Tuple

class CorpusLoader:
    def __init__(self, corpus_path: str = '../data'):
        self.corpus_path = corpus_path
        self.corpus = {}
        self.index = {}
        self._load_corpus()
    
    def _load_corpus(self):
        if not os.path.exists(self.corpus_path):
            print(f"Warning: Corpus path not found at {self.corpus_path}")
            return
        
        for domain in ['hackerrank', 'claude', 'visa']:
            domain_path = os.path.join(self.corpus_path, domain)
            if os.path.exists(domain_path):
                self.corpus[domain] = self._load_domain_docs(domain_path)
            else:
                self.corpus[domain] = []
        
        self._build_index()
    
    def _load_domain_docs(self, domain_path: str) -> List[Dict]:
        docs = []
        
        for filename in os.listdir(domain_path):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(domain_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        doc = json.load(f)
                        doc['source_file'] = filename
                        docs.append(doc)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return docs
    
    def _build_index(self):
        for domain, docs in self.corpus.items():
            self.index[domain] = {}
            for doc in docs:
                title = doc.get('title', '').lower()
                content = doc.get('content', '').lower()
                keywords = doc.get('keywords', [])
                
                for keyword in keywords:
                    kw_lower = keyword.lower()
                    if kw_lower not in self.index[domain]:
                        self.index[domain][kw_lower] = []
                    self.index[domain][kw_lower].append(doc)
    
    def search(self, domain: str, query: str, top_k: int = 3) -> List[Dict]:
        if domain not in self.corpus or not self.corpus[domain]:
            return []
        
        query_terms = query.lower().split()
        docs = self.corpus[domain]
        
        scored_docs = []
        for doc in docs:
            score = 0
            title = doc.get('title', '').lower()
            content = doc.get('content', '').lower()
            keywords = [kw.lower() for kw in doc.get('keywords', [])]
            
            for term in query_terms:
                if term in title:
                    score += 3  # Higher weight for title matches
                if term in content:
                    score += 1
                if any(term in kw for kw in keywords):
                    score += 2
            
            if score > 0:
                scored_docs.append((doc, score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:top_k]]
    
    def get_all_docs(self, domain: str) -> List[Dict]:
        return self.corpus.get(domain, [])
