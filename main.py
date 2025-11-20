import json
import re
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, inspect
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


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
# STEP 2: Convert Natural Language → SQL
# ---------------------------------------------------------
def text_to_sql(schema, prompt):
    SYSTEM_PROMPT = """
    You are an expert SQL generator.
    Given a database schema and a user question, generate a VALID SQLite SQL query.
    RULES:
    - Use ONLY tables & columns provided.
    - Do NOT hallucinate.
    - Output SQL only.
    - No explanation.
    - No <think> tags.
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Schema:\n{schema}\n\nQuestion: {user_prompt}\n\nSQL Query:")
    ])

    model = OllamaLLM(
        model="llama3:8b",
        temperature=0,
        timeout=10
    )

    chain = prompt_template | model

    raw = chain.invoke({"schema": schema, "user_prompt": prompt})

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
        return f"❌ SQL Execution Error:\n{e}\n\nGenerated SQL:\n{sql_query}"


# ---------------------------------------------------------
# STEP 4: Natural-language explanation
# ---------------------------------------------------------
def explain_results(user_query, data):
    if isinstance(data, str):
        return data  # Already an error text

    model = OllamaLLM(model="llama3:8b", temperature=0)

    prompt = f"""
    User Question: {user_query}
    SQL Output: {data}

    Explain these results clearly and simply.
    Only use factual information from the result.
    """

    return model.invoke(prompt).strip()


# ---------------------------------------------------------
# STEP 5: Detect if data is chartable → DataFrame
# ---------------------------------------------------------
def detect_and_prepare_chart(data):
    if not isinstance(data, list) or len(data) == 0:
        return None

    df = pd.DataFrame(data)

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) == 0:
        return None

    return df
