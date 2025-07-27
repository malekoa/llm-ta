import json
import numpy as np
from bot.embeddings import embed_chunk
from bot.database import Database

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_documents(db: Database, query: str, top_k: int = 5):
    query_embedding = embed_chunk(query)

    # Include document_id to join with document name
    db.cursor.execute("""
        SELECT dc.id, dc.content, d.filename, dc.embedding
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE dc.embedding IS NOT NULL
    """)
    rows = db.cursor.fetchall()

    results = []
    for chunk_id, content, filename, embedding_json in rows: 
        embedding = json.loads(embedding_json)
        sim = cosine_similarity(query_embedding, embedding)
        results.append((chunk_id, content, filename, sim))

    # Sort by similarity
    results.sort(key=lambda x: x[3], reverse=True)  # sort by sim
    return results[:top_k]