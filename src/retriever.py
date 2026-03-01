from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import faiss 
from sentence_transformers import SentenceTransformer
from parser import parse_xml


@dataclass
class RetrievedArticle:
    """A class representing a retrieved article."""
    pmcid: str
    pmid: str
    title: str
    body: str
    score: float
    
class Retriever: 
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", fallback_chars: int = 1500, normalize: bool = True):
        self.model = SentenceTransformer(model_name)
        self.fallback_chars = fallback_chars
        self.normalize = normalize
        
    def build_embed_text(self, article: Dict[str, Any]) -> Tuple[str, str]:
        """Build an embedding for the article."""
        title = (article.get("title", "")).strip()
        body = (article.get("body", "")).strip()
        
        snippet = body[:300]
        fallback = body[-self.fallback_chars:]
        embed_text = f"{title}\n{fallback}"
        return snippet, embed_text
    
    def embed(self, texts: str) -> np.ndarray:
        vecs = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
        ).astype("float32")
        vecs = faiss.normalize_L2(vecs)
        return vecs