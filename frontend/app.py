import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Travel Assistant",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Travel Assistant")
st.markdown("Your intelligent travel companion powered by AI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything about travel!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call backend API
                response = requests.post(
                    "http://backend:8000/chat",
                    json={"user_input": prompt},
                    timeout=30
                )
                response.raise_for_status()
                
                assistant_response = response.json()["content"]
                st.markdown(assistant_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Sorry, I'm having trouble connecting to my brain 🧠. Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

# Sidebar with information
with st.sidebar:
    st.markdown("## About")
    st.markdown("""
    This Travel Assistant can help you with:
    - 🌤️ Weather information
    - 🔍 Travel destination research
    - 💬 General travel advice
    - 📍 Local attractions and recommendations
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
