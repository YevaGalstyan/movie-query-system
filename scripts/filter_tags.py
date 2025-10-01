import pandas as pd

# Load the movies dataset
movies_df = pd.read_csv("../data/movies_links_merged.csv")

# Load the movies + tags dataset
movie_tags_df = pd.read_csv("../data/raw/tags.csv")

filtered_movies = movie_tags_df[movie_tags_df["movieId"].isin(movies_df["movieId"])]

filtered_movies.to_csv("../data/tags_filtered.csv", index=False)

print(filtered_movies.head())
