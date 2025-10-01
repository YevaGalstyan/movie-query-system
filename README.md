# Movie Chat Assistant
A Streamlit-based chat application that uses the Gemini model to intelligently query a consolidated movie database (built from MovieLens and TMDb data) using dynamic SQL generation.

## Features
- Intelligent Querying: Uses the Gemini model for a two-step process: classifying user intent and translating natural language questions into executable PostgreSQL queries.

- Rich Data Aggregation: Combines foundational movie data (titles, genres, tags) from the MovieLens dataset with rich contextual data (taglines, overviews) fetched from The Movie Database (TMDb) API.

- Asynchronous Database Operations: Utilizes asyncpg for efficient, non-blocking interaction with the PostgreSQL database.

- Detailed Thought Process: Exposes the model's classification and generated SQL query via a UI expander for transparency and debugging.

## Project Sctructure

| File                      | Description                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `app.py`                    | The main Streamlit application file. Handles the UI, chat flow, and calls the core async query handler ( `handle_prompt`).               |
| `config.py`               | Stores configuration parameters, including PostgreSQL database credentials (`DB_CONFIG`) and the Gemini API key/URL.                    |
| `gemini_api.py`           | Contains helper functions to call the Gemini API for three main tasks: question classification, SQL query generation, and general Q&A. |
| `db_utils.py`               | Utility functions for database interaction, including an experimental function for querying movies using vector embeddings.            |
| `connect_movies_links.py`   | Merges MovieLens `movies.csv`` and `links.csv`, extracts the year, and processes genres.                                                    |
| `connect_movies_tagline.py` | Uses `tmdbId` from the merged links to fetch and aggregate `tagline` and `overview` data from the TMDb API.                                  |
| `filter_tags.py`            | Filters the MovieLens `tags.csv` to only include tags for the movies present in the final dataset.                                       |
| `connect_movies_tags.py `   | Aggregates the filtered tags per movie into a single column.                                                                           |
| `upload_movies.py `         | Combines all prepared CSVs and inserts the final, comprehensive movie data into the PostgreSQL  `movies_full` table.                     |
| `upload_embedding.py`       | Experimental script to generate and upload embeddings for movie overviews/taglines using the `pgvector` extension.                      |## Project Sctructure

## Data Pipeline: Consolidation & Augmentation
The project's database is a result of combiing data from two distinct sources:

1. [MovieLens Full Dataset](https://grouplens.org/datasets/movielens/):
    - Movies: Provides `movieId`, `title`, and `genres`.
    - Links: Provides the mapping between `movieId` and external IDs, specifically the `tmdbId`.
    - Tags: Provides user-submitted tags for movies.

2. [TMDb (The Movie Database) API](https://developer.themoviedb.org/docs/getting-started):
    - A custom script (`connect_movies_tagline.py`) was executed to call the TMDb API using the `tmdbId` obtained from the MovieLens `links` table. This process successfully scraped essential descriptive text:
        - `tagline`: A memorable, catchy phrase for the movie.
        - `overview`: The plot summary.

All this data is ultimately merged and stored in a single table in the PostgreSQL database named `movies_full`.

### Data access 
[Access Movie Data Files](https://drive.google.com/drive/folders/1AK6cJD3qYW0cEgKjJSfpYNUuxLrEfaKK?usp=sharing)

The raw datasets used in this project, as well as the processed CSV files that were ultimately uploaded to the PostgreSQL `movies_full` table, are available via Google Drive:
- Raw Data: Original MovieLens CSV files (`movies.csv`, `links.csv`, `tags.csv`) and any other source files.
- Processed Data: Filtered and consolidated CSV files used to populate the PostgreSQL database.

**Note:** These files are provided for reproducibility. Ensure your PostgreSQL database is set up as per the project structure before running the scripts.

### Primary Database Schema (`movies_full`)
The Gemini model is provided with the following table schema to inform its SQL generation:
```
movies_full(
   movieId INT PRIMARY KEY,
   tmdbId INT,
   title TEXT,
   genres TEXT,
   year INT,
   tags TEXT,
   tagline TEXT,
   overview TEXT
   -- embedding VECTOR(384) -- (For the experimental feature)
)
```

## LLM Architecture (Gemini Integration)
The `app.py` uses the Gemini model in a sequential chain of thought to fulfill user requests:
1. **Classification**: The initial call to Gemini determines if the user's prompt is a **movie-related question**.
2. **SQL Generation** (If Movie-Related): If the prompt is movie-related, a second call instructs Gemini to generate a valid PostgreSQL query against the `movies_full` table to fetch the required data.
3. **Database Query**: The generated SQL is executed. The results (a list of movies) are retrieved and displayed in a Streamlit `dataframe`/`table`.
4. **General Answer** (If Not Movie-Related): If the prompt is classified as non-movie-related, a final call to Gemini provides a general, helpful text answer.

## The Embedding Experiment (Vector Search)
An experimental feature was developed to explore semantic search capabilities using vector embeddings.
- **Methodology**:
    1. The `upload_embedding.py` script generated 384-dimensional vector embeddings for the combined `tagline` and `overview` text of each movie using the `all-MiniLM-L6-v2` Sentence Transformer model.
    2. These embeddings were stored in a `VECTOR` column within the movies_full table, utilizing the PostgreSQL extension `pgvector`.
    3. User queries were also embedded (`db_utils.py` - `get_question_embedding`).
    4. A vector similarity search was performed using the standard `ORDER BY embedding <-> $1` (Euclidean distance) operator to find the most semantically similar movies.
- **Status**:
    While technically implemented (`upload_embedding.py` and `db_utils.py's` query_movies_by_embedding), testing revealed that the results from the vector similarity search were not consistently accurate or relevant enough to provide a high-quality movie recommendation experience. Therefore, the primary functionality relies on the structured output of Gemini-generated SQL. The embedding feature is currently disabled in the main app.py chat flow but remains available for future iteration and refinement.

## Additional Notes

1. **Gemini API Credentials**  
   A personal Gemini API key and URL must be added to the `config.py` file in order to connect to the model and enable query generation. Without these credentials, the application will not be able to execute intelligent SQL queries.

2. **Test Queries and Results**  
   The repository includes a `test.md` file demonstrating example queries, the LLM’s responses, and explanations of the outputs. This file can be used to validate the functionality and understand how the system interprets different prompts.

3. **Project Paper**  
   A short academic paper, `Movie_Query_System.pdf`, is included. It is a two-page document summarizing the project, methodology, and results, providing a concise reference for the system and its capabilities.
