import openai
from dotenv import load_dotenv
import streamlit as st
import os
import time

load_dotenv()

client = openai.OpenAI()
model = "gpt-4o-mini"

# Initialize Streamlit session state
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = "asst_uI5y5h9G1Jvb75TGS1rXmxCL"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "thread_4v8gACWGuXFaXXsHmMNcvBUo"
if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_run_id" not in st.session_state:
    st.session_state.last_run_id = None

st.set_page_config(layout="wide")

# Sidebar for file uploads
with st.sidebar:
    st.title("Document Upload")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    # Handle file uploads and deletions
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_files:
                # Process new file upload
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Create a new vector store if it doesn't exist
                if not st.session_state.vector_store_id:
                    vector_store = client.beta.vector_stores.create(name="Study Documents")
                    st.session_state.vector_store_id = vector_store.id
                
                # Upload the file to the vector store
                with open(uploaded_file.name, "rb") as file_stream:
                    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                        vector_store_id=st.session_state.vector_store_id,
                        files=[file_stream]
                    )
                
                # Update the assistant with the vector store
                assistant = client.beta.assistants.update(
                    assistant_id=st.session_state.assistant_id,
                    tool_resources={
                        "file_search": {
                            "vector_store_ids": [st.session_state.vector_store_id]
                        }
                    }
                )
                
                st.success(f"File '{uploaded_file.name}' uploaded and added to the vector store.")
                
                # Clean up the temporary file
                os.remove(uploaded_file.name)
                
                # Add the file name to the list of uploaded files
                st.session_state.uploaded_files.append(uploaded_file.name)
        
        # Handle file deletions
        for file in st.session_state.uploaded_files[:]:
            if file not in [f.name for f in uploaded_files]:
                st.session_state.uploaded_files.remove(file)
                st.success(f"File '{file}' deleted.")
                st.rerun()

# Main chat interface
st.title("Study AI Helper")

# Function to process user input and get assistant response
def process_user_input(input_text):
    # Create a message
    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=input_text,
    )
    
    # Create a run
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.session_state.assistant_id,
        instructions="Please address the user as your 'Study Buddy'",
    )
    st.session_state.last_run_id = run.id  # Store the run ID
    
    # Wait for the run to complete with a loading indicator
    with st.spinner("Generating response..."):
        while run.status not in ['completed', 'failed', 'cancelled', 'expired']:
            time.sleep(1)  # Wait for 1 second before checking again
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
    
    if run.status == 'completed':
        # Retrieve and display the assistant's response
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        last_message = messages.data[0]
        response = last_message.content[0].text.value
        return response
    else:
        return f"Run failed with status: {run.status}"

# Function to handle user input
def handle_input():
    user_message = st.session_state.user_input
    if user_message:
        st.session_state.chat_history.append(("User", user_message))
        assistant_response = process_user_input(user_message)
        st.session_state.chat_history.append(("Assistant", assistant_response))
        st.session_state.user_input = ""  # This will clear the input for the next render

# Create a container for the chat history
chat_container = st.container()

# Input area at the bottom
st.text_input("Type your question here:", key="user_input", on_change=handle_input)
start_chat = st.button("Start Chat", on_click=handle_input)

# Display chat history
with chat_container:
    for i, (role, message) in enumerate(st.session_state.chat_history):
        if role == "User":
            st.markdown(f'<div class="user-message"><b>You:</b> {message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message"><b>Assistant:</b> {message}</div>', unsafe_allow_html=True)

# Custom CSS to style the chat messages
st.markdown("""
<style>
.user-message {
    background-color: #2b313e;
    color: #ffffff;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.assistant-message {
    background-color: #3c4043;
    color: #ffffff;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Display chat history
with chat_container:
    for i, (role, message) in enumerate(st.session_state.chat_history):
        if role == "User":
            st.markdown(f'<div class="user-message"><b>You:</b> {message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message"><b>Assistant:</b> {message}</div>', unsafe_allow_html=True)

# Display run steps (for debugging)
if st.button("Show Run Steps"):
    if st.session_state.last_run_id:
        logs = client.beta.threads.runs.steps.list(
            thread_id=st.session_state.thread_id,
            run_id=st.session_state.last_run_id
        )
        st.write(f"Run Steps: {logs.data}")
    else:
        st.write("No run has been executed yet.")
