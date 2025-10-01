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
