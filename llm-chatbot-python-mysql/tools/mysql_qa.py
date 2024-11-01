import streamlit as st
from llm import llm
from db import database, db_url
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine, inspect
import pandas as pd

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
You are an expert in MySQL who translates user questions into SQL queries to find answers about company data in the database.
Translate the user's questions according to the database schema.
Use only the types of relationships and properties that exist in the given schema. Do not use other types of relationships or properties that are not in the provided schema.

Provide answers primarily in Thai, but some financial terms may remain in English. If you don't know the answer, respond with 'I don't know.'

Fine Tuning:
1.FilteredEODData: table for company financial statement data, available quarterly (de, ebitAccum, ebitQuarter, epsAccum, epsQuarter, financingCashFlow, fixedAssetTurnover, hasQuarter, hasYear, investingCashFlow, netProfitAccum, netProfitMarginAccum, netProfitMarginQuarter, netProfitQuarter, operatingCashFlow, paidupShareCapital, roa, roe, shareholderEquity, totalAssetTurnover, totalAssets, totalEquity, totalExpensesAccum, totalExpensesQuarter, totalLiabilities, totalRevenueAccum, totalRevenueQuarter)
  financial_statements: tablefor daily company stock price data (average, close, high, low, open, prior, totalVolume), with the date information in the URI, e.g., uri: http://example.org/stock_value_CPALL_2024-01-25.
2.for example "ขอข้อมูลopenของหุ้นBBLในวันที่2023-09-01" qurey = SELECT open FROM FilteredEODData WHERE symbol = 'BBL' AND date = '2023-09-01' LIMIT 1;
3.Query:เขียนใน```Query```
   
Schema:
{schema}

Question:
{question}

Mysql Query:
```

```
"""

# Define the tools for SQL generation and execution
execute_query = QuerySQLDataBaseTool(db=database)
write_query = create_sql_query_chain(llm, database)
# Create the prompt template
sql_prompt = PromptTemplate.from_template(MYSQL_GENERATION_TEMPLATE)

# Define the LangChain QA chain
mysql_qa = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | sql_prompt
    | llm
    | StrOutputParser()
)

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
schema1 = get_schema(engine)

from sqlalchemy import text

def mysql_qa_function(input_text):
    schema_str = format_schema(schema1)  # Convert schema to string format
    
    try:
        # Generate the SQL query using the LangChain QA chain
        generated_result = mysql_qa.invoke({
            "question": input_text,
            "schema": schema_str
        })

        # Extract the SQL query from the generated result
        query_start = generated_result.find("```\n") + 4  # Locate the start of the SQL query
        query_end = generated_result.find("\n```", query_start)  # Locate the end of the SQL query
        query = generated_result[query_start:query_end].strip()  # Extract the query string
        
        # Define the USE statement and the query
        use_statement = "USE financials;"
        full_query = f"{use_statement}\n{query}"
        print(f"Generated SQL Query: {full_query}")  # Debugging: Print the final SQL query

        # Connect to the database and execute the query
        with engine.connect() as connection:
            # Execute the USE statement
            connection.execute(text(use_statement))
            # Execute the main query
            result = connection.execute(text(query))
            data = result.fetchall()

        # Convert the result to a pandas DataFrame for better readability
        df = pd.DataFrame(data, columns=result.keys())

        return df  # Return the DataFrame with the results
    
    except Exception as e:
        print(f"Error generating or executing the query: {e}")
        return f"Error: Unable to generate or execute the query due to {str(e)}"

# Export the tool
__all__ = ["mysql_qa_function"]
