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

import time  # Import the time module

# # Function to generate response
# def generate_response(user_input):
#     try:
#         # Start the timer
#         start_time = time.time()

#         # Call the agent executor with appropriate arguments
#         response = agent_executor.invoke({
#             "input": user_input,
#             "chat_history": st.session_state.get("chat_history", []),
#             "agent_scratchpad": ""
#         })
#         # End the timer
#         end_time = time.time()
        
#         # Calculate the time taken
#         time_taken = end_time - start_time

#         # Print the response and time taken for debugging
#         print(f"Agent response: {response}")
#         print(f"Time taken: {time_taken:.5f} seconds")

#         # Ensure 'output' key is handled
#         return response.get('output', 'No output found')
#     except Exception as e:
#         print(f"Error Agent generating response: {e}")
#         return f"Error Agent : Unable to generate response due to {str(e)}"
    
import tiktoken
import time

# เลือกโทเค็นไลเซอร์ที่ตรงกับโมเดลของคุณ
encoding = tiktoken.get_encoding("cl100k_base")  # เปลี่ยนตามโมเดลที่ใช้

def count_tokens(text):
    return len(encoding.encode(text))

def generate_response(user_input):
    try:
        # นับโทเค็นในคำถามที่ผู้ใช้ป้อน
        input_token_count = count_tokens(user_input)
        print(f"Input token count: {input_token_count}")

        # เริ่มจับเวลาตอบสนอง
        start_time = time.time()

        # เรียก agent เพื่อสร้างคำตอบ
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": st.session_state.get("chat_history", []),
            "agent_scratchpad": ""
        })

        # จับเวลาสิ้นสุด
        end_time = time.time()
        time_taken = end_time - start_time

        # นับโทเค็นในคำตอบที่ได้
        output_text = response.get('output', 'No output found')
        output_token_count = count_tokens(output_text)
        print(f"Output token count: {output_token_count}")
        print(f"Time taken: {time_taken:.5f} seconds")

        # ส่งกลับคำตอบและจำนวนโทเค็นทั้งหมด
        total_token_count = input_token_count + output_token_count
        print(f"Total token count for the query: {total_token_count}")
        return output_text

    except Exception as e:
        print(f"Error generating response: {e}")
        return f"Error: Unable to generate response due to {str(e)}"
