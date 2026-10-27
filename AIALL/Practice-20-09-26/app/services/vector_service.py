"""
Vector RAG Service for Financial Regulatory & Credit Filings
In a hackathon:
  You index multi-page PDF/TXT reports.
  Here, we implement an In-Memory Vector Store with Cosine Similarity,
  pre-loaded with realistic BNP Paribas corporate banking documents!
"""
import numpy as np
from typing import List, Dict, Any


class FinancialVectorStore:
    def __init__(self):
        # Realistic corporate filings & regulatory guidelines
        self.documents: List[Dict[str, Any]] = [
            {
                "id": "DOC-BNP-001",
                "title": "BNP Paribas CIB Syndicated Lending Guidelines 2025",
                "section": "Section 3.1: Leverage Ratio Limits",
                "content": "For corporate facilities exceeding EUR 50M, maximum permitted Net Debt to EBITDA is 3.5x. Any deviation requires Credit Committee approval and an interest spread step-up of 75 bps.",
                "tags": ["leverage", "covenant", "syndicated_loan"]
            },
            {
                "id": "DOC-BNP-002",
                "title": "EU Corporate Sustainability Due Diligence Directive (CSDDD)",
                "section": "Article 15: Transition Plan Compliance",
                "content": "Obligation for large corporate entities to adopt and put into effect a climate transition plan compatible with 1.5°C Paris Agreement targets. Failure to comply restricts ESG-linked financing access.",
                "tags": ["esg", "compliance", "csddd", "green_finance"]
            },
            {
                "id": "DOC-BNP-003",
                "title": "Sanction Screening & Beneficial Ownership Policy",
                "section": "KYC Standard 8: Indirect Control",
                "content": "An entity is considered sanctioned if 50% or more is owned directly or indirectly by one or more sanctioned persons, or if effective control is exerted through subsidiary holding companies.",
                "tags": ["kyc", "aml", "sanctions", "beneficial_ownership"]
            },
             {
                "id": "DOC-BNP-004",
                "title": "TotalEnergies SE - Q4 Financial Covenant Disclosure",
                "section": "Note 14: Contingent Liabilities & Guarantees",
                "content": "TotalEnergies SE guarantees outstanding debt of EUR 320M for joint venture subsidiary Total Solar Africa B.V. Debt maturity is March 2028 with debt service coverage ratio at 1.8x.",
                "tags": ["guarantee", "subsidiary", "covenant", "totalenergies"]
            },
            {
                "id": "DOC-BNP-005",
                "title": "Airbus SE - Supplier Chain & Risk Exposure Filing",
                "section": "Item 7: Raw Material Price Hedging",
                "content": "Airbus maintains interest rate hedging derivatives and currency swaps to mitigate EUR/USD fluctuations across its European delivery contracts.",
                "tags": ["hedging", "market_risk", "airbus"]
            }
        ]

         # Simple keyword/semantic weight generator for offline zero-friction execution
        self._build_index()
    def _build_index(self):
        # Create vocabulary for term-frequency embedding vectors
        all_words = set()
        for doc in self.documents:
            words = doc["content"].lower().replace(".", "").replace(",", "").split()
            all_words.update(words)
        self.vocab = list(all_words)
        self.vocab_map = {w: i for i, w in enumerate(self.vocab)}
         # Build document vectors
        self.doc_vectors = np.zeros((len(self.documents), len(self.vocab)))
        for idx, doc in enumerate(self.documents):
            for word in doc["content"].lower().replace(".", "").replace(",", "").split():
                if word in self.vocab_map:
                    self.doc_vectors[idx, self.vocab_map[word]] += 1.0
            # Normalize vectors
            norm = np.linalg.norm(self.doc_vectors[idx])
            if norm > 0:
                self.doc_vectors[idx] /= norm
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant document chunks via cosine similarity
        """
        query_vec = np.zeros(len(self.vocab))
        query_words = query.lower().replace(".", "").replace(",", "").split()
         for word in query_words:
            if word in self.vocab_map:
                query_vec[self.vocab_map[word]] += 1.0
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec /= q_norm
            scores = np.dot(self.doc_vectors, query_vec)
        else:
            # Fallback if no matching vocabulary
            scores = np.array([0.1] * len(self.documents))
        # Rank indices by score descending
        ranked_indices = np.argsort(scores)[::-1][:top_k]
         results = []
        for idx in ranked_indices:
            results.append({
                "document_id": self.documents[idx]["id"],
                "title": self.documents[idx]["title"],
                "section": self.documents[idx]["section"],
                "content": self.documents[idx]["content"],
                "relevance_score": round(float(scores[idx]), 4)
            })
        return results
    
    def add_document(self, title: str, section: str, content: str, tags: List[str] = None) -> str:
        """
        Dynamically ingest a new policy or borrower filing
        """
        doc_id = f"DOC-USER-{len(self.documents) + 1:03d}"
        self.documents.append({
            "id": doc_id,
            "title": title,
            "section": section,
            "content": content,
            "tags": tags or []
        })
        self._build_index()
        return doc_id
        
vector_service = FinancialVectorStore()
