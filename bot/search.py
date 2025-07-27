import json
import numpy as np
from bot.embeddings import embed_chunk
from bot.database import Database

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_documents(db: Database, query: str, top_k: int = 5):
    # 1. Embed the query
    query_embedding = embed_chunk(query)

    # 2. Fetch all chunks
    db.cursor.execute("SELECT id, content, embedding FROM document_chunks WHERE embedding IS NOT NULL")
    rows = db.cursor.fetchall()

    # 3. Compute similarity for each chunk
    results = []
    for chunk_id, content, embedding_json in rows:
        embedding = json.loads(embedding_json)
        sim = cosine_similarity(query_embedding, embedding)
        results.append((chunk_id, content, sim))

    # 4. Sort by similarity & return top_k
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]