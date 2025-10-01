## LLM Query Benchmark Set

This set of 25 natural language queries is designed to benchmark the LLM's ability to accurately translate complex, ambiguous, and multi-criteria user requests into correct PostgreSQL queries against the `movies_full` table.

### Target Table Schema

```sql
movies_full(
   movieId INT PRIMARY KEY,
   tmdbId INT,
   title TEXT,
   genres TEXT,
   year INT,
   tags TEXT,
   tagline TEXT,
   overview TEXT
)
````


### Category 1: Simple Metadata Retrieval
Tests basic filtering, exact matching, and sorting on single or primary columns.

| ID | Query                                                                    | Primary Field(s) Tested             | Objective                                             |
| - | ------------------------------------------------------------------------ | ----------------------------------- | ----------------------------------------------------- |
| 1 | What are all the movies released in the year 1995?                       | year                                | Simple numerical match.                               |
| 2 | Find the titles of the 10 oldest movies in the database.                 | year, Sorting (ASC), LIMIT          | Basic sorting and retrieval limit.                    |
| 3 | List all movies that are categorized as 'Comedy'.                        | genres                              | Simple text search/containment within genres.         |
| 4 | Show the movie details for the title 'Toy Story'.                        | title                               | Exact string match on the primary title field.        |
| 5 | Which movies have the word 'Revenge' in their title?                     | title                               | Partial string match (fuzzy search/LIKE operator).    |
| 6 | Give me the movieId and title for any movies with the genre 'Film-Noir'. | genres, Projection                  | Testing field projection (SELECT clause).             |
| 7 | Find the newest 5 Sci-Fi movies.                                         | genres, year, Sorting (DESC), LIMIT | Simple filter combined with sorting.                  |
| 8 | What is the tagline for the movie 'The Matrix'?                          | title, Projection                   | Exact match for a specific, single piece of metadata. |



### Category 2: Complex Multi-Criteria Requests
Tests combining multiple logical conditions (AND/OR), complex text matching, and negation (NOT).

| ID | Query                                                                                                                            | Primary Field(s) Tested               | Objective                                                           |
| -- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------- |
| 9  | List all movies that are tagged with 'dystopia' AND are in the 'Sci-Fi' genre.                                                   | tags, genres                          | Complex AND operation across two text fields.                       |
| 10 | Find movies released after 2010 that are either 'Action' OR 'Thriller'.                                                          | year, genres                          | Combined numerical/text filtering with OR logic.                    |
| 11 | Show me movies with the word 'future' in their overview but not in their tagline.                                                | overview, tagline                     | Complex text search with negation/exclusion.                        |
| 12 | Get the titles of movies that are tagged 'time travel' and were released before 2000.                                            | tags, year                            | AND operation combining text and numerical data.                    |
| 13 | Retrieve all movie titles and overviews for movies that have an overview containing the phrases 'alien invasion' or 'space war'. | overview                              | Complex OR operation within a large text field.                     |
| 14 | Which movies are NOT categorized as 'Documentary' but were released in 2022?                                                     | genres, year, Negation (NOT LIKE/<> ) | Testing negation logic combined with a simple filter.               |
| 15 | Find the 7 most recent movies that contain both the 'Horror' and 'Mystery' genres.                                               | genres, year, Sorting, LIMIT          | Multiple criteria within a single text field combined with sorting. |
| 16 | Give me all details for any movie tagged 'superhero' that was released between 2005 and 2015.                                    | tags, year                            | Range condition (BETWEEN or >= and <=) combined with text matching. |

### Category 3: Queries Not Supported by Database Schema
Tests the LLM's handling of requests for data not present in the movies_full table (producers, actors, or production companies).

| ID  | Query                                                | Primary Field(s) Tested | Objective                                                                                       |
| --- | ---------------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------ |
| 17  | List all movies produced by Steven Spielberg.       | N/A                    | Tests LLM's ability to recognize missing producer/director information in the database.         |
| 18  | Show movies where the production company is Warner Bros. | N/A                | Tests LLM's ability to recognize missing production company information in the database.        |
| 19  | Find romantic movies starring Meryl Streep.        | N/A                    | Tests LLM's ability to handle requests for actors/cast when such information is not available. |


## LLM Query Benchmarking
| ID  | Expected SQL Query | Query Received / LLM Output |
|-----|------------------|----------------------------|
| 1   | `SELECT * FROM movies_full WHERE year = 1995;` | `SELECT * FROM movies_full WHERE year = 1995;` |
| 2   | `SELECT title FROM movies_full ORDER BY year ASC LIMIT 10;` | `SELECT title FROM movies_full ORDER BY year ASC LIMIT 10;` |
| 3   | `SELECT * FROM movies_full WHERE genres LIKE '%Comedy%';` | `SELECT title FROM movies_full WHERE genres LIKE '%Comedy%';` |
| 4   | `SELECT * FROM movies_full WHERE title = 'Toy Story';` | `SELECT * FROM movies_full WHERE title LIKE 'Toy Story';` |
| 5   | `SELECT * FROM movies_full WHERE title LIKE '%Revenge%';` | `SELECT title FROM movies_full WHERE title LIKE '%Revenge%';` |
| 6   | `SELECT movieId, title FROM movies_full WHERE genres LIKE '%Film-Noir%';` | `SELECT movieId, title FROM movies_full WHERE genres LIKE '%Film-Noir%';` |
| 7   | `SELECT * FROM movies_full WHERE genres LIKE '%Sci-Fi%' ORDER BY year DESC LIMIT 5;` | `SELECT title, year FROM movies_full WHERE genres LIKE '%Sci-Fi%' ORDER BY year DESC LIMIT 5;` |
| 8   | `SELECT tagline FROM movies_full WHERE title = 'The Matrix';` | `SELECT tagline FROM movies_full WHERE title LIKE '%The Matrix%';` |
| 9   | `SELECT * FROM movies_full WHERE tags LIKE '%dystopia%' AND genres LIKE '%Sci-Fi%';` | `SELECT title FROM movies_full WHERE tags LIKE '%dystopia%' AND genres LIKE '%Sci-Fi%';` |
| 10  | `SELECT * FROM movies_full WHERE year > 2010 AND (genres LIKE '%Action%' OR genres LIKE '%Thriller%');` | `SELECT * FROM movies_full WHERE year > 2010 AND (genres LIKE '%Action%' OR genres LIKE '%Thriller%');` |
| 11  | `SELECT * FROM movies_full WHERE overview ILIKE '%future%' AND (tagline IS NULL OR tagline NOT ILIKE '%future%');` | `SELECT title, overview, tagline FROM movies_full WHERE overview ILIKE '%future%' AND (tagline IS NULL OR tagline NOT ILIKE '%future%');` |
| 12  | `SELECT title FROM movies_full WHERE tags LIKE '%time travel%' AND year < 2000;` | `SELECT title FROM movies_full WHERE tags LIKE '%time travel%' AND year < 2000;` |
| 13  | `SELECT title, overview FROM movies_full WHERE overview ILIKE '%alien invasion%' OR overview ILIKE '%space war%';` | `SELECT title, overview FROM movies_full WHERE overview ILIKE '%alien invasion%' OR overview ILIKE '%space war%';` |
| 14  | `SELECT * FROM movies_full WHERE genres NOT LIKE '%Documentary%' AND year = 2022;` | `SELECT title, year, genres FROM movies_full WHERE genres NOT LIKE '%Documentary%' AND year = 2022;` |
| 15  | `SELECT * FROM movies_full WHERE genres LIKE '%Horror%' AND genres LIKE '%Mystery%' ORDER BY year DESC LIMIT 7;` | `SELECT title, year, genres FROM movies_full WHERE genres LIKE '%Horror%' AND genres LIKE '%Mystery%' ORDER BY year DESC LIMIT 7;` |
| 16  | `SELECT * FROM movies_full WHERE tags LIKE '%superhero%' AND year BETWEEN 2005 AND 2015;` | `SELECT * FROM movies_full WHERE tags LIKE '%superhero%' AND year BETWEEN 2005 AND 2015;` |
| 17  | N/A (cannot query producer/director) | `I am sorry, but the database schema does not contain information about movie producers or directors.` |
| 18  | N/A (cannot query production company) | `I am sorry, but the database schema does not include information about movie production companies.` |
| 19  | N/A (cannot query actors/cast) | `I cannot fulfill this request. The database schema does not include information about actors or cast members. I can only search for movies by title, genre, year, tags, tagline, or overview.` |
