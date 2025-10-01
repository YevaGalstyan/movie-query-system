import pandas as pd

# Load datasets
movies = pd.read_csv("../data/raw/movies.csv")
links = pd.read_csv("../data/raw/links.csv")

links["tmdbId"] = links["tmdbId"].astype("Int64").astype(str)

# Replace "(no genres listed)" with empty string before splitting
movies["genres"] = movies["genres"].replace("(no genres listed)", "")
movies["genres"] = movies["genres"].apply(lambda x: x.split("|") if x != "" else [])

# -------------------
# Remove movies with no genres
# -------------------
movies = movies[movies["genres"].map(len) > 0]

# Extract year using regex
movies["year"] = movies["title"].str.extract(r"\((\d{4})\)$").astype("Int64")

# Remove the year from the title itself
movies["title"] = movies["title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)

# Merge on movieId
merged = pd.merge(movies, links, on="movieId", how="inner")

# Select only the columns you want
final_df = merged[["movieId", "tmdbId", "title", "genres", "year"]]

# Save to new CSV
final_df.to_csv("../data/movies_links_merged.csv", index=False)

print(final_df.head())

# -------------------
# Create genre mapping file
# -------------------
# Flatten all genre lists and get unique values
all_genres = sorted(set(g for sublist in merged["genres"] for g in sublist))

# Make a DataFrame with ids for each genre
genre_map = pd.DataFrame({
    "genreId": range(1, len(all_genres) + 1),
    "genre": all_genres
})

# Save genre map
genre_map.to_csv("../data/genres.csv", index=False)
