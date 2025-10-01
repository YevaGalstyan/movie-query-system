import pandas as pd

# Load the filtered tags CSV
tags_df = pd.read_csv("../data/tags_filtered.csv")

# Group by movieId and aggregate tags into a list
movie_tags_aggregated = (
    tags_df.groupby("movieId")["tag"]
    .apply(list)
    .reset_index()
    .rename(columns={"tag": "tags"})
)

# Save to CSV
movie_tags_aggregated.to_csv("../data/movie_tags_aggregated.csv", index=False)

print(movie_tags_aggregated.head())
