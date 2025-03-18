import streamlit as st
from llm import llm
from db import database, db_url
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine, inspect, text
import pandas as pd
import logging

# Configure logging to log to a file for debugging
logging.basicConfig(filename='sql_query_logs.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Construct the database URL
MYSQL_HOST = st.secrets["MYSQL_HOST"]
MYSQL_USER = st.secrets["MYSQL_USER"]
MYSQL_PASSWORD = st.secrets["MYSQL_PASSWORD"]
MYSQL_DB = st.secrets["MYSQL_DB"]


db_url = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

# Create the SQLAlchemy engine
engine = create_engine(db_url)

# Create an instance of SQLDatabase using the SQLAlchemy engine
database = SQLDatabase(engine)

MYSQL_GENERATION_TEMPLATE = """
You are an expert in MySQL who translates user input into SQL queries to find answers about company data in the database.
Translate the user's input according to the database schema.
Use only the types of relationships and properties that exist in the given schema. Do not use other types of relationships or properties that are not in the provided schema.

Provide answers primarily in Thai, but some financial terms may remain in English. If you don't know the answer, respond with 'I don't know.'

Fine Tuning:
1.FilteredEODData: table for company financial statement data, available quarterly ...
2.For example "ขอข้อมูลopenของหุ้นBBLในวันที่2023-09-01" query = SELECT open FROM FilteredEODData WHERE symbol = 'BBL' AND date = '2023-09-01' LIMIT 1;
3.Query: เขียนใน```Query`
   
Schema:
{schema}


Mysql Query:
```

```
"""

# Define the tools for SQL generation and execution
execute_query = QuerySQLDataBaseTool(db=database)

# Create the prompt template
sql_prompt = PromptTemplate.from_template(MYSQL_GENERATION_TEMPLATE)
write_query = create_sql_query_chain(llm, database)



# Function to fetch schema
def get_schema(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    schema = {}
    for table in tables:
        columns = inspector.get_columns(table)
        schema[table] = {col['name']: str(col['type']) for col in columns}
    return schema

# Convert schema to string format for prompt
def format_schema(schema):
    formatted = ""
    for table, columns in schema.items():
        formatted += f"Table: {table}\n"
        for column, type_ in columns.items():
            formatted += f"  - Column: {column}, Type: {type_}\n"
    return formatted

# Fetch schema from the database
schema_dict = get_schema(engine)  # This returns a dictionary
schema_ = format_schema(schema_dict)  # Convert dictionary to formatted string

# Define the LangChain QA chain
mysql_qa = (
    RunnableLambda(lambda inputs: {
        "query": write_query.invoke(inputs["query"]),
        "schema": schema_
    }).assign(
        result=itemgetter("query") | execute_query
    )
    | sql_prompt
    | llm
    | StrOutputParser()
)
from sqlalchemy import text

def mysql_qa_function(input):
    try:
        # Debug input structure
        logging.debug(f"Input question: {input}")
        logging.debug(f"Schema passed to invoke: {schema_}")
        if not isinstance(input, str):
            raise ValueError("The input question must be a string.")

        # Prepare input data with "question"
        input_data = {
            "question": input,  # Ensure compatibility with the tool
            "schema": schema_
        }
        logging.debug(f"Data passed to mysql_qa: {input_data}")

        # Generate SQL query
        generated_result = mysql_qa.invoke(input_data)
        logging.debug(f"Generated result: {generated_result}")

        # Extract query
        query_start = generated_result.find("```\n") + 4
        query_end = generated_result.find("\n```", query_start)
        query = generated_result[query_start:query_end].strip()

        # Construct full query
        use_statement = "USE financials;"
        full_query = f"{use_statement}\n{query}"
        logging.debug(f"Executing query: {full_query}")

        # Execute the query
        with engine.connect() as connection:
            connection.execute(text(use_statement))
            result = connection.execute(text(query))
            data = result.fetchall()

        # Return DataFrame
        if data:
            return pd.DataFrame(data, columns=result.keys()), query
        else:
            return pd.DataFrame(), query

    except Exception as e:
        logging.error(f"Error during query generation or execution: {e}")
        return pd.DataFrame(), ""


# Export the tool
__all__ = ["mysql_qa_function"]
