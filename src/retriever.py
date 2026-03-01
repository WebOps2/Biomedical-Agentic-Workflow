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
    title: str
    snippet: str
    score: float
    
class Retriever: 
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", fallback_chars: int = 1500, normalize: bool = True):
        self.model = SentenceTransformer(model_name)
        self.fallback_chars = fallback_chars
        self.normalize = normalize
        self.index: Optional[faiss.Index] = None
        self.meta_data: List[Dict[str, Any]] = [] 
        
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
        faiss.normalize_L2(vecs)
        return vecs
    
    def build_index(self, xml_dir: str) -> faiss.Index:
        "Takes xml files converts them to embeddings and builds an index"
        xml_dir = Path(xml_dir)
        xml_files = sorted(xml_dir.rglob("*.xml"))
        if not xml_files:
            raise FileNotFoundError(f"No XML files found in {xml_dir}")
        
        articles : List[Dict[str, Any]] = []
        embedded_texts : List[str] = []
        
        for xml_file in xml_files:
            try:
                article = parse_xml(xml_file)
            except Exception as e:
                print(f"Error parsing {xml_file}: {e}")
                continue
            snippet, embed_text = self.build_embed_text(article)
            articles.append(article)
            embedded_texts.append(embed_text)
            
            self.meta_data.append(
                {
                    "pmcid": article["pmcid"],
                    "title": article["title"],
                    "snippet": snippet,
                }
            )
            
        if not articles or not embedded_texts:
            raise ValueError("No articles or embedded texts found")
             
        vecs = self.embed(embedded_texts)
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(vecs)
    
    def retrieve(self, query: str, k: int) -> List[RetrievedArticle]:  
        "Retrieves articles based on a query"
        if self.index is None:
            raise ValueError("Index not built")
        
        query_vec = self.embed([query])
        scores, indices = self.index.search(query_vec, k)
        print(scores)
        print(indices)
        
        result : List[RetrievedArticle] = []
        
        for scores, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            result.append(RetrievedArticle(
                pmcid=self.meta_data[idx]["pmcid"],
                title=self.meta_data[idx]["title"],
                snippet=self.meta_data[idx]["snippet"],
                score=scores,
            ))
        return result
        # return [self.meta_data[i] for i in indices[0]]
    
retriever = Retriever()
index = retriever.build_index("data/pmc_sample")
res = retriever.retrieve("The semi-annual meeting of the Quincy Medical Societyt", k=1)
print(res)