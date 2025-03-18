from llm import llm
from llm import embeddings
from db import database
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub
# from tools.vector import get_company_industry
from tools.mysql_qa import mysql_qa_function


import streamlit as st
from llama_index.core import ServiceContext, StorageContext, VectorStoreIndex, load_index_from_storage
from langchain_groq import ChatGroq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_core.prompts import PromptTemplate
from utils import get_session_id

# Initialize the LLM and embedding models
embed_model = embeddings

from langchain.schema import SystemMessage, HumanMessage

# Define the simple function
def simple_function(input_text):
    return f"Received input: {input_text}"

# Create the Tool instance
General_Chat = Tool.from_function(
    name="General Chat",
    description="For general conversations about financial information not covered by other tools",
    func=simple_function
)

# company_industry_Tool = Tool.from_function(
#     name="company industry Search",
#     description="Use to find out which industry a company belongs to",
#     func=get_company_industry
# )


mysql_qa_Tool = Tool.from_function(
    name="search company's data",
    description="Use to find company's financial ratios and financial information using queries.",
    func=mysql_qa_function
)


tools = [
    General_Chat,
    mysql_qa_Tool
]
# company_industry_Tool,

prompt_template = PromptTemplate.from_template("""
You are a financial expert tasked with providing accurate and comprehensive information and advice related to financial matters. This includes company data, investments, market conditions, and economic trends.

Language Instructions:
- Provide answers primarily in Thai.
- Use English for specific financial terms when necessary.

Source of Information:
- Use only the information available in the context provided.
- Do not use knowledge learned independently.

TOOLS:
You can use the following tools, but avoid using General_Chat if possible:

{tools}

To use a tool, please follow these steps:

1. Determine if the information needed to answer the question is available in the context.
2. If the information is not available, decide if the tool is appropriate for retrieving it.
3. If the tool should be used, follow this format:

```
Thought: Is it necessary to use a tool? Yes
Action: The action to be taken should be one of [{tool_names}]
Action Input: Information used for the action
Observation: The result of the action
```

When you have an answer to provide to the user or if it's unnecessary to use a tool, use the following format:
                                               
```
Thought: Is it necessary to use a tool? No
Final Answer: [Your answer here]
```

Begin!

Previous conversation history:
{chat_history}

New message: {input}
{agent_scratchpad}
""")

# Create the agent instance
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt_template
)

# Setup the agent executor with error handling
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    prompt=prompt_template,
    verbose=True,
    handle_parsing_errors=True  # Enable error handling for parsing issues
)


def generate_response(question):
    try:
        # เรียกใช้ mysql_qa_function เพื่อนำ SQL query และผลลัพธ์
        df_results, sql_query = mysql_qa_function(question)
        
        # สร้างข้อความตอบกลับจากผลลัพธ์
        if not df_results.empty:
            response = df_results.to_string(index=False)
        else:
            response = "No data found for the query."
        
        return response, sql_query, df_results

    except Exception as e:
        return f"Error: Unable to process the query due to {e}", None, None

