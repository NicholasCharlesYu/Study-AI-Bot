import openai
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
import os
import streamlit as st
import json
import requests

load_dotenv()

client = openai.OpenAI()
model = "gpt-4o-mini"


#== Create File Search Assistant ==
# assistant = client.beta.assistants.create(
#     name="Study Buddy",
#     description="Your personal study assistant",
#     instructions="""You are a helpful study assistant who knows a lot about understanding research papers.
#     Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
#     Cross-reference information for additional insights and answer related questions comprehensively.
#     Analyze the papers, noting strengths and limitations.
#     Respond to queries effectively, incorporating feedback to enhance your accuracy.
#     Handle data securely and update your knowledge base with the latest research.
#     Adhere to ethical standards, respect intellectual property, and provide users with guidance on any limitations.
#     Maintain a feedback loop for continuous improvement and user support.
#     Your ultimate goal is to facilitate a deeper understanding of complex scientific material, making it more accessible and comprehensible.""",
#     model=model,
#     tools=[{"type": "file_search"}],
# )
# assistant_id = assistant.id
# print(assistant_id)

# # Create a vector store caled "Textbooks"
# vector_store = client.beta.vector_stores.create(name="Textbooks")
 
# # Ready the files for upload to OpenAI
# file_paths = ["./AIMA.pdf"]
# file_streams = [open(path, "rb") for path in file_paths]
 
# # Upload the files, add them to the vector store,
# # and poll the status of the file batch for completion.
# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#   vector_store_id=vector_store.id, files=file_streams
# )
# print(file_batch.status)
# print(file_batch.file_counts)

# # Update the assistant with the vector store
# assistant = client.beta.assistants.update(
#   assistant_id=assistant.id,
#   tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
# )

# # Create a thread
# thread = client.beta.threads.create()
# print(thread.id)

# Hardcoded assistant and thread ids
assistant_id = "asst_uI5y5h9G1Jvb75TGS1rXmxCL"
thread_id = "thread_4v8gACWGuXFaXXsHmMNcvBUo"

# Create a message
message = "What is AI?"
message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message,
)
 
# Create a run and print response
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread_id,
    assistant_id=assistant_id,
    instructions="Please address the user as your 'Study Buddy'",
)
if run.status == 'completed': 
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    last_message = messages.data[0]
    response = last_message.content[0].text.value
    print(f"Assistant Response: {response}")
else:
  print(run.status)

#== Check Logs ==
logs = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Run Steps: {logs.data[0]}")