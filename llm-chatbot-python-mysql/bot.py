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

# Submit handler
def handle_submit(message):
    """
    Submit handler:

    You will modify this method to talk with an LLM and provide
    context using data from MYSQL.
    """

    # Handle the response
    with st.spinner('Thinking...'):
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)
        


# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)
    