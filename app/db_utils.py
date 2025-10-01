import asyncpg
from config import DB_CONFIG
from sentence_transformers import SentenceTransformer
from pgvector.asyncpg import register_vector

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_question_embedding(question: str):
    """
    Returns 384-dim embedding vector for a user question
    """
    return embedding_model.encode(question).astype(float).tolist()

async def query_movies_by_embedding(question: str):
    """
    Returns top_k movies semantically similar to question using pgvector
    """
    embedding_vector = get_question_embedding(question)
    conn = await asyncpg.connect(**DB_CONFIG)
    await register_vector(conn)
    try:
        sql = """
        SELECT movieId, title, tagline, overview, genres, tags
        FROM movies_full
        ORDER BY embedding <-> $1
        """
        rows = await conn.fetch(sql, embedding_vector)
        return [dict(r) for r in rows] if rows else []
    finally:
        await conn.close()
