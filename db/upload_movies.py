import asyncio
import asyncpg
import pandas as pd

# ----------------------------
# 1️⃣ Load movie CSV with year
# ----------------------------
MOVIES_CSV = "../data/movies_links_merged.csv"
movies_df = pd.read_csv(MOVIES_CSV)
movies_df = movies_df.dropna(subset=['movieId'])
movies_df['movieId'] = movies_df['movieId'].astype('Int64')
movies_df['tmdbId'] = movies_df['tmdbId'].astype('Int64')
for col in ['title', 'genres']:
    movies_df[col] = movies_df[col].where(movies_df[col].notna(), None)
movies_df['year'] = movies_df['year'].astype('Int64')

# ----------------------------
# 2️⃣ Load movie tags CSV
# ----------------------------
TAGS_CSV = "../data/movie_tags_aggregated.csv"
tags_df = pd.read_csv(TAGS_CSV)
tags_df = tags_df.dropna(subset=['movieId'])
tags_df['movieId'] = tags_df['movieId'].astype('Int64')
tags_df['tags'] = tags_df['tags'].where(tags_df['tags'].notna(), "")

# Merge movies and tags on movieId
df_main = pd.merge(movies_df, tags_df, on='movieId', how='left')
df_main['tags'] = df_main['tags'].fillna("")

# ----------------------------
# 3️⃣ Load overview and tagline CSV
# ----------------------------
OVERVIEW_CSV = "../data/overview_tagline.csv"
df_extra = pd.read_csv(OVERVIEW_CSV, usecols=['movieId', 'tagline', 'overview'])
df_extra = df_extra.dropna(subset=['movieId'])
df_extra['movieId'] = df_extra['movieId'].astype('Int64')
for col in ['tagline', 'overview']:
    df_extra[col] = df_extra[col].where(df_extra[col].notna(), None)

# Merge main df with extra info
df_final = pd.merge(df_main, df_extra, on='movieId', how='left')

# ----------------------------
# 4️⃣ Database configuration
# ----------------------------
DB_CONFIG = {
    "user": "yevagalstyan",
    "password": None,
    "database": "movies_db",
    "host": "localhost",
    "port": 5432
}

# ----------------------------
# 5️⃣ Async insertion
# ----------------------------
async def main():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    # Create a single table for all movie info
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS movies_full (
            movieId INT PRIMARY KEY,
            tmdbId INT,
            title TEXT,
            genres TEXT,
            year INT,
            tags TEXT,
            tagline TEXT,
            overview TEXT
        )
    """)
    
    # Insert into the combined table
    for _, row in df_final.iterrows():
        movie_id = int(row['movieId'])
        tmdb_id = int(row['tmdbId']) if pd.notna(row['tmdbId']) else None
        title = row['title']
        genres = row['genres']
        year = int(row['year']) if pd.notna(row['year']) else None
        tags_text = row['tags']
        tagline = row['tagline']
        overview = row['overview']

        await conn.execute("""
            INSERT INTO movies_full(movieId, tmdbId, title, genres, year, tags, tagline, overview)
            VALUES($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (movieId) DO UPDATE
            SET tmdbId = EXCLUDED.tmdbId,
                title = EXCLUDED.title,
                genres = EXCLUDED.genres,
                year = EXCLUDED.year,
                tags = EXCLUDED.tags,
                tagline = EXCLUDED.tagline,
                overview = EXCLUDED.overview;
        """, movie_id, tmdb_id, title, genres, year, tags_text, tagline, overview)
        
        print(f"✅ Inserted/Updated movieId {movie_id}")

    print("✅ All data loaded!")
    await conn.close()

# ----------------------------
# 6️⃣ Run async function
# ----------------------------
if __name__ == "__main__":
    asyncio.run(main())
