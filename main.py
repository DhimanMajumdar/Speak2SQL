# step1: extract schema

from sqlalchemy import column, create_engine,inspect, schema
import json

db_url="sqlite:///amazon.db"

def extract_schema(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)
    schema = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [col['name'] for col in columns]
    return json.dumps(schema)


# step2: text to sql (deepseek with ollama)

# build streamlit frontend