import requests
import pandas as pd
import time

# -------------------------
# Configuration
# -------------------------
API_KEY = '7739166833e78cc9e4161a7912dc77c6'
BASE_URL = 'https://api.themoviedb.org/3/movie/'

# -------------------------
# Load movies CSV
# -------------------------
movies_df = pd.read_csv("../data/movies_links_merged.csv")
print(f"Loaded {len(movies_df)} movies.")

# Function to fetch movie details from TMDb
def fetch_movie_details(tmdb_id):
    try:
        url = f"{BASE_URL}{tmdb_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                'tmdbId': tmdb_id,
                'tagline': data.get('tagline', ''),
                'overview': data.get('overview', '')
            }
        else:
            print(f"Warning: Failed to fetch TMDb ID {tmdb_id}, status code {response.status_code}")
            return {'tmdbId': tmdb_id, 'tagline': '', 'overview': ''}
    except Exception as e:
        print(f"Error fetching TMDb ID {tmdb_id}: {e}")
        return {'tmdbId': tmdb_id, 'tagline': '', 'overview': ''}

# -------------------------
# Fetch details for each movie
# -------------------------
movie_details_list = []
for idx, tmdb_id in enumerate(movies_df['tmdbId']):
    if pd.isna(tmdb_id):
        continue  # Skip missing TMDb IDs
    movie_details_list.append(fetch_movie_details(int(tmdb_id)))
    if (idx + 1) % 50 == 0:
        print(f"Processed {idx + 1}/{len(movies_df)} movies...")
        time.sleep(0.25)  # Small delay to avoid rate limits

# Convert to DataFrame
movie_details_df = pd.DataFrame(movie_details_list)

# Merge with original movies dataset to keep movieId, title, genres, year
final_df = movies_df[['movieId', 'tmdbId']].merge(movie_details_df, on='tmdbId', how='left')

final_df = final_df.drop(columns=['tmdbId'])

# Save to CSV
final_df.to_csv("../data/movies_with_tagline_overview.csv", index=False)
print("Saved movies_with_tagline_overview.csv successfully.")
