import asyncio
import asyncpg
from sentence_transformers import SentenceTransformer
from pgvector.asyncpg import register_vector

DB_CONFIG = {
    "user": "yevagalstyan",
    "password": None,
    "database": "movies_db",
    "host": "localhost",
    "port": 5432
}

model = SentenceTransformer('all-MiniLM-L6-v2')

async def add_embeddings_to_db():
    conn = await asyncpg.connect(**DB_CONFIG)
    await register_vector(conn)  # <--- registers vector type with asyncpg

    rows = await conn.fetch("SELECT movieId, tagline, overview FROM movies_full")

    for row in rows:
        movie_id = row.get('movieid')
        text = " ".join(filter(None, [row.get('tagline'), row.get('overview')]))
        if not text.strip():
            continue

        embedding_vector = model.encode(text).astype(float).tolist()

        await conn.execute(
            'UPDATE movies_full SET embedding = $1 WHERE movieId = $2',
            embedding_vector,  # now asyncpg knows how to handle it
            movie_id
        )
        print(f"✅ Added embedding for movieId {movie_id}")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(add_embeddings_to_db())
