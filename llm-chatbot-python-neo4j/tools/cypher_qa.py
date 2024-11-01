import streamlit as st
from llm import llm
from fkg import graph
import pandas as pd
from neo4j import GraphDatabase

from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

query='.'
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher queries to find answers about company data in the database.
Translate the user's questions according to the database schema.
Use only the types of relationships and properties that exist in the given schema. Do not use other types of relationships or properties that are not in the provided schema.

data in knowledge graph :
**Nodes:**
- `Company`: Represents each company.
  - Properties: `name` (String), `symbol` (String)
- `FinancialStatement`: Represents the financial statement details of each company.
  - Properties: `year` (String), `quarter` (String)
- `MarketData`: Represents stock market-related data for the companies.
  - Properties: `date` (String)
- `Period`: Represents the time period for the financial data.
  - Properties: `year` (String), `quarter` (String), `date` (String)
- **Financial Nodes:**
  - `Assets`: Total assets.
    - Properties: `totalAssets` (Float)
  - `Liabilities`: Total liabilities.
    - Properties: `totalLiabilities` (Float)
  - `Equity`: Shareholder equity and total equity.
    - Properties: `shareholderEquity` (Float), `totalEquity` (Float)
  - `Revenue`: Revenue data.
    - Properties: `totalRevenueQuarter` (Float), `totalRevenueAccum` (Float)
  - `Expenses`: Expenses data.
    - Properties: `totalExpensesQuarter` (Float), `totalExpensesAccum` (Float)
  - `CashFlow`: Cash flow data.
    - Properties: `operatingCashFlow` (Float), `investingCashFlow` (Float), `financingCashFlow` (Float)
  - `FinancialRatio`: Various financial ratios.
    - Properties: `type` (String), `value` (Float)
    - Types: 
      - `ROE` (Return on Equity)
      - `ROA` (Return on Assets)
      - `DE` (Debt to Equity Ratio)
      - `PE` (Price to Earnings Ratio)
      - `PBV` (Price to Book Value)
  - `MarketRatio`: Various market ratios.
    - Properties: `type` (String), `value` (Float)
    - Types:
      - `PE` (Price to Earnings Ratio)
      - `PB` (Price to Book Ratio)
      - `Dividend_Yield` (Dividend_Yield)
      - `Beta` (Volatility Measure)
      - `Market_Cap`
      - `Volume_Turnover`
- **Market Data Nodes:**
  - `Price`: Price-related data.
    - Properties: `prior` (Float), `open` (Float), `high` (Float), `low` (Float), `close` (Float), `average` (Float)
  - `Volume`: Volume-related data.
    - Properties: `aomVolume` (Float), `aomValue` (Float), `trVolume` (Float), `trValue` (Float), `totalVolume` (Float), `totalValue` (Float)
  - `MarketRatio`: Various market ratios.
    - Properties: `type` (String), `value` (Float)
**Relationships:**
- `Company` to `FinancialStatement`: `HAS_FINANCIAL_STATEMENT`
- `FinancialStatement` to Financial Nodes: `HAS_ASSETS`, `HAS_LIABILITIES`, `HAS_EQUITY`, `HAS_REVENUE`, `HAS_EXPENSES`, `HAS_CASH_FLOW`, `HAS_RATIO`
- `FinancialStatement` to `Period`: `IS_FOR_PERIOD`
- `Company` to `MarketData`: `HAS_MARKET_DATA`
- `MarketData` to Market Data Nodes: `HAS_PRICE`, `HAS_VOLUME`, `HAS_RATIO`
- `MarketData` to `Period`: `IS_FOR_PERIOD`

Parameters: only use this parameter Schema and qusetion 
  Schema:
  {schema}
  query:
  {query}

Fine Tuning:
1.For stock tickers or company names, ensure that you follow the proper case sensitivity and return values as they appear in the database.
2.useing data in knowledge graph for write query
3.directly select value that want to know if database have, don't calculate it
4.when write query only use English
5.if you want to use price use like this (p:Price{{symbol: "ADVANC"}})
6.if you want to use MarketRatio use like this (m:MarketRatio{{symbol: "ADVANC"}})

  
Example Cypher Statements:
1.อัตราส่วนการคืนทุน (ROE) ของบริษัทADVANC ในไตรมาสที่ 1 ของปี 2019 คือเท่าไหร่:
```
MATCH (c:Company {{symbol: 'ADVANC'}})-[:HAS_FINANCIAL_STATEMENT]->(fs:FinancialStatement {{year: '2019', quarter: '1'}})
MATCH (fs)-[:HAS_RATIO]->(r:FinancialRatio {{type: 'ROE'}})
RETURN r.value AS ROE
```

2.สัดส่วนหนี้สินต่อทุน (DE) ของบริษัทADVANC ในไตรมาสที่ 1 ของปี 2019 คือเท่าไหร่:
```
MATCH (c:Company {{symbol: 'ADVANC'}})-[:HAS_FINANCIAL_STATEMENT]->(fs:FinancialStatement {{year: '2019', quarter: '1'}})
MATCH (fs)-[:HAS_RATIO]->(r:FinancialRatio {{type: 'DE'}})
RETURN r.value AS DebtToEquity
```

3.ราคาปิดของหุ้นADVANC ในวันที่ 1 กันยายน 2023 คือเท่าไหร่:
```
MATCH (md:MarketData{{date: "2023-09-01"}})-[:HAS_PRICE]->(p:Price{{symbol: "ADVANC"}})
RETURN p.close AS closingPrice
```

4.อัตราการจ่ายเงินปันผล (Dividend Yield) ของหุ้น BBL ในวันที่ 1 กันยายน 2023 คือเท่าไหร่:
```
MATCH (mr:MarketRatio{{symbol: 'BBL',type: "Dividend Yield",date: "2023-09-01"}})
RETURN mr.value as DividendYield
```

5.แนวโน้มของรายได้รวมของบริษัท ADVANC มีการเปลี่ยนแปลงอย่างไรในช่วงเวลาที่ผ่านมาจากข้อมูลทางการเงิน:
```
MATCH (c:Company {{symbol: 'ADVANC'}})-[:HAS_FINANCIAL_STATEMENT]->(fs:FinancialStatement)
MATCH (fs)-[:HAS_REVENUE]->(r:Revenue)
RETURN fs.year, fs.quarter, r.totalRevenueAccum
ORDER BY fs.year, fs.quarter
```

6.เปรียบเทียบผลตอบแทนต่อผู้ถือหุ้น (ROE) ของบริษัท ADVANC ในปี 2019 กับปี 2022:
```
MATCH (fs_2019:FinancialStatement {{year: '2019'}})-[:HAS_RATIO]->(roe_2019:FinancialRatio {{symbol: 'ADVANC',type: 'ROE'}})
MATCH (fs_2022:FinancialStatement {{year: '2022'}})-[:HAS_RATIO]->(roe_2022:FinancialRatio {{symbol: 'ADVANC',type: 'ROE'}})
RETURN roe_2019.value AS ROE_2019, roe_2022.value AS ROE_2022
```

7.เปรียบเทียบรายได้รวมในไตรมาสของบริษัท ADVANC กับบริษัท CPALL ในไตรมาสที่ 3 ปี 2021:
```
MATCH (adv_fs:FinancialStatement {{year: '2021', quarter: '3'}})-[:HAS_REVENUE]->(adv_r:Revenue{{symbol: 'ADVANC'}})
MATCH (cpall_fs:FinancialStatement {{year: '2021', quarter: '3'}})-[:HAS_REVENUE]->(cpall_r:Revenue{{symbol: 'CPALL'}})
RETURN adv_r.totalRevenueQuarter AS ADVANC_TotalRevenue, cpall_r.totalRevenueQuarter AS CPALL_TotalRevenue
```

Respond with only the generated Cypher query:

"""


# Create a new prompt for financial queries
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

# Instantiate the GraphCypherQAChain for the financial knowledge graph
cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,  # Connect this to your financial Neo4j graph
    verbose=True,
    cypher_prompt=cypher_prompt
)

# Function to fetch schema from Neo4j
def get_schema_from_neo4j(driver):
    with driver.session() as session:
        # Example: Get all labels
        labels_result = session.run("CALL db.labels()")
        labels = [record["label"] for record in labels_result]

        # Example: Get all relationships
        rels_result = session.run("CALL db.relationshipTypes()")
        relationships = [record["relationshipType"] for record in rels_result]

        schema = {
            "labels": labels,
            "relationships": relationships
        }

    return schema

# Convert schema to string format for prompt
def format_schema(schema):
    formatted = "Labels:\n"
    for label in schema["labels"]:
        formatted += f"  - {label}\n"
        
    formatted += "Relationships:\n"
    for relationship in schema["relationships"]:
        formatted += f"  - {relationship}\n"
        
    return formatted

# Connect to Neo4j database
NEO4J_URI = st.secrets["NEO4J_URI"]
NEO4J_USER = st.secrets["NEO4J_USERNAME"]
NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Fetch schema from the Neo4j database
schema = get_schema_from_neo4j(driver)
schema_str = format_schema(schema)  # Convert schema to string format

# Define a function to handle Cypher queries
def cypher_qa_function(input_text):
    try:
        # Generate the Cypher query using the LangChain QA chain
        generated_result = cypher_qa.invoke({
            "query": input_text,
            "schema": schema_str,
        })

        return generated_result['result']

    except Exception as e:
        print(f"Error generating or executing the query: {e}")
        return f"Error: Unable to generate or execute the query due to {str(e)}"

# Export the function
__all__ = ["cypher_qa_function"]
