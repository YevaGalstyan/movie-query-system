import asyncpg
import streamlit as st
import time
import json
import asyncio

from config import DB_CONFIG
from db_utils import query_movies_by_embedding
from gemini_api import ask_gemini_classification, ask_gemini_answer, ask_gemini_sql
from pgvector.asyncpg import register_vector

st.title("🎬 Movie Chat Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []


async def handle_prompt(prompt: str):
    """Main async logic for handling a user query."""
    thought_process = ""

    # Step 1: Check if it's a movie question
    classification = await ask_gemini_classification(prompt)
    thought_process = f"Classification JSON:\n```json\n{json.dumps(classification, indent=2)}\n```"

    if classification.get("is_movie_question"):
        # Step 2: Ask Gemini to generate SQL query
        sql_json = await ask_gemini_sql(prompt)
        sql_query = sql_json.get("sql_query", "")
        thought_process += f"\n\nGenerated SQL:\n```sql\n{sql_query}\n```"

        # Step 3: Run SQL query if valid
        movie_info = []
        try:
            if sql_query.strip():
                # If Gemini provided SQL, run it directly
                conn = await asyncpg.connect(**DB_CONFIG)
                await register_vector(conn)
                rows = await conn.fetch(sql_query)
                movie_info = [dict(r) for r in rows]
                await conn.close()
            else:
                movie_info = []
                thought_process += "\n\n(SQL query was empty.)"
        except Exception as e:
            movie_info = []
            thought_process += f"\n\n⚠️ SQL Error: {str(e)}"

        content_text = f"Fetched {len(movie_info)} result(s)." if movie_info else "No movies found."

        return content_text, movie_info, thought_process

    else:
        # Non-movie question → ask Gemini for an answer
        answer_json = await ask_gemini_answer(prompt)
        content_text = answer_json.get("answer_text", "LLM did not provide an answer.")
        return content_text, None, thought_process


# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg.get("content", ""))
        if msg.get("movie_info"):
            if len(msg["movie_info"]) > 1:
                st.dataframe(msg["movie_info"])
            else:
                st.table(msg["movie_info"])
        if "thought" in msg:
            with st.expander("💡 Thought Process"):
                st.markdown(msg["thought"])


# Chat input
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        time.sleep(0.5)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")
        time.sleep(1)

        # Run async query handler
        content_text, movie_info, thought_process = asyncio.run(handle_prompt(prompt))

        # Show results
        placeholder.markdown(content_text)

        if movie_info:
            if len(movie_info) > 1:
                st.dataframe(movie_info)
            else:
                st.table(movie_info)

        with st.expander("💡 Thought Process", expanded=False):
            st.markdown(thought_process)

        st.session_state.messages.append({
            "role": "assistant",
            "content": content_text,
            "movie_info": movie_info,
            "thought": thought_process
        })
