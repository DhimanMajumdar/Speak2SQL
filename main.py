import json
import re
import sqlite3
from sqlalchemy import create_engine, inspect
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM


DB_URL = "sqlite:///amazon.db"


# ---------------------------------------------------------
# STEP 1: Extract DB Schema
# ---------------------------------------------------------
def extract_schema(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)

    schema = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [col["name"] for col in columns]

    return json.dumps(schema, indent=2)


# ---------------------------------------------------------
# STEP 2: Convert Natural Language → SQL (Llama3, safe)
# ---------------------------------------------------------
def text_to_sql(schema, prompt):
    SYSTEM_PROMPT = """
    You are an expert SQL generator. 
    Given a database schema and a user question, generate a VALID SQLite SQL query.
    - Use ONLY tables & columns from the schema.
    - Do NOT hallucinate table names.
    - Output only SQL. No explanation.
    - No <think> or reasoning tags.
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Schema:\n{schema}\n\nQuestion: {user_prompt}\n\nSQL Query:")
    ])

    model = OllamaLLM(
        model="llama3:8b",      # SQL-friendly model (no think tags)
        temperature=0,
        timeout=10              # ⬅ prevents infinite hanging
    )

    chain = prompt_template | model

    raw = chain.invoke({"schema": schema, "user_prompt": prompt})

    # Remove any stray reasoning tokens (safety)
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", raw).strip()

    return cleaned


# ---------------------------------------------------------
# STEP 3: Execute SQL safely
# ---------------------------------------------------------
def get_data_from_database(prompt):
    schema = extract_schema(DB_URL)

    try:
        sql_query = text_to_sql(schema, prompt)
    except Exception as e:
        return f"❌ ERROR generating SQL:\n{e}"

    try:
        conn = sqlite3.connect("amazon.db")
        cursor = conn.cursor()
        rows = cursor.execute(sql_query).fetchall()
        conn.close()
        return rows

    except Exception as e:
        return (
            f"❌ SQL Execution Error:\n{e}\n\n"
            f"Generated SQL was:\n{sql_query}"
        )
