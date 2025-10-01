import httpx
import json
import re
from config import API_KEY, API_URL

# --- Gemini API Call Function ---
async def call_gemini_api(prompt: str, is_json: bool = False, system_prompt: str = ""):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]} if system_prompt else None,
        "generationConfig": {
            "responseMimeType": "application/json" if is_json else "text/plain"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{API_URL}?key={API_KEY}", json=payload)
            response.raise_for_status()
            result = response.json()
            candidate = result.get("candidates", [])[0]
            part = candidate.get("content", {}).get("parts", [])[0]
            if is_json:
                return json.loads(part.get("text", "{}"))
            return part.get("text", "").strip()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}, {e.response.text}")
        return {} if is_json else "API_ERROR"
    except Exception as e:
        print(f"An error occurred: {e}")
        return {} if is_json else "API_ERROR"

# --- Helpers for specific tasks ---
async def ask_gemini_classification(user_question: str):
    system_prompt = f"""
You are an assistant that determines whether a user's question is about movies.
Answer in JSON format ONLY.

Question: "{user_question}"

Instructions:
- JSON format: {{ "is_movie_question": true/false, "reason": "Explain briefly why." }}
"""
    return await call_gemini_api(prompt=user_question, is_json=True, system_prompt=system_prompt)

async def ask_gemini_answer(user_question: str):
    system_prompt = f"""
You are a helpful assistant. Answer naturally.
Output JSON only.

Question: "{user_question}"

Instructions:
- JSON format: {{ "action": "answer", "answer_text": "..." }}
"""
    return await call_gemini_api(prompt=user_question, is_json=True, system_prompt=system_prompt)

async def ask_gemini_sql(user_question: str):
    system_prompt = f"""
You are an assistant that translates natural language movie-related questions into SQL queries.
The database schema is:

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

Return JSON only in the following format:
{{
  "sql_query": "SELECT ...",
  "reason": "Briefly explain how the query answers the question."
}}

Rules:
- Only use the columns listed above.
- If filtering is unclear, return a broad query (e.g., ORDER BY rating DESC LIMIT 10).
- Always output syntactically correct PostgreSQL SQL.
- When query by name use LIKE for partial matches.
- If the information is not in the schema, return a string explaining the limitation.
"""
    return await call_gemini_api(prompt=user_question, is_json=True, system_prompt=system_prompt)
