import streamlit as st
import openai
import time

# Set OpenAI API key
# Initialize OpenAI client
client = openai.Client()

def display_conversation(placeholder, conversation):
    with placeholder.container():
        for message in conversation:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def display_response_word_by_word(assistant_response):
    words = assistant_response.split()
    for i in range(len(words)):
        # Update the conversation with each additional word
        partial_response = " ".join(words[:i+1])
        st.session_state.conversation[-1]["content"] = partial_response
        display_conversation(conversation_placeholder, st.session_state.conversation)
        time.sleep(0.04)  # Adjusted for proportional delay

    # Update the conversation with the entire response at the end to ensure correct formatting
    st.session_state.conversation[-1]["content"] = assistant_response
    display_conversation(conversation_placeholder, st.session_state.conversation)


# Define the page layout
st.set_page_config(
    layout="wide",
    page_title="Conversation with Estedic"
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)


# Streamlit application setup
st.image('./logo.png') 
st.markdown(
    "<h1>Chat with us and learn more about Estedic! <sup style='font-size:.5em; vertical-align: super; padding-left: 5px; color: yellow'>Beta</sup></h1>",
    unsafe_allow_html=True,
)
st.header("In this beta website feature, we trained James, our large language model-powered bot, to learn more about Estedic and surface resources matched with your interest in data management.")


# Initialize or retrieve session state
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None
    st.session_state.conversation = []      

# User input
user_input = st.chat_input("👋🏻 Hello! How can I help?")

with st.chat_message("assistant"):
    multi ='''Welcome! I'm here to answer any questions you have about Estedic. Here are some example prompts you can try (or just type whatever your question is!):   
    • I'd like to learn more about Estedic   
    • I'd like to learn more about using AI with enterprise data   
    • I'd like to schedule an appointment'''
    st.markdown(multi)

# Create a placeholder for conversation history
conversation_placeholder = st.empty()

if user_input:
    # Add user input to conversation history and display it
    st.session_state.conversation.append({"role": "user", "content": user_input})
    display_conversation(conversation_placeholder, st.session_state.conversation)

    # Create a new thread if not exists
    if not st.session_state.thread_id:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Submitting user message to thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, 
        role="user", 
        content=user_input
    )

    # Creating a run with the assistant
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.secrets["ASSISTANT_ID"]
    )
    
    # Wait for the response
    while run.status in ["queued", "in_progress"]:
        time.sleep(0.2)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    # Retrieve the assistant's response
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    for message in messages.data:
        if message.role == 'assistant':
            assistant_message = message.content[0].text.value
            # Add an empty assistant message to the conversation
            st.session_state.conversation.append({"role": "assistant", "content": ""})
            # Display the response word by word
            display_response_word_by_word(assistant_message)
            break


