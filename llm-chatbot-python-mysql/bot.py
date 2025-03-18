import streamlit as st
from utils import write_message
from agent import generate_response

# Page Config
st.set_page_config("Finance bot", page_icon=":coin:")

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีครับ ผมคือผู้ช่วยการเงินของคุณ! มีอะไรให้ช่วยในเรื่องการเงินบ้างไหมครับ?"},
    ]
if "interaction_log" not in st.session_state:
    st.session_state.interaction_log = []  # To store detailed log of each interaction

# Submit handler
def handle_submit(user_input):
    # Handle the response
    with st.spinner('Thinking...'):
        # Call the agent
        response_data = generate_response(user_input)
        # Extract individual pieces from the response dictionary
        # response = response_data['response']
        # chain_interaction = response_data['chain_interaction']
        # sql_query = response_data['sql_query']
        # result_data = response_data['result_data']

        # # Now you can use these variables as needed
        # print(f"Agent Response: {response}")
        # print(f"Chain Interaction: {chain_interaction}")
        # print(f"SQL Query: {sql_query}")
        # print(f"Result Data: {result_data}")
        write_message('assistant', response_data)
        

    
# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)
