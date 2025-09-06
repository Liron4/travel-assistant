import streamlit as st
import requests
import json
import uuid

st.set_page_config(
    page_title="Travel Assistant",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Travel Assistant")
st.markdown("Your intelligent travel companion powered by AI with conversation memory")

# Initialize session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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
                # Call backend API with session ID
                response = requests.post(
                    "http://backend:8000/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id
                    },
                    timeout=30
                )
                response.raise_for_status()
                
                response_data = response.json()
                assistant_response = response_data["response"]
                
                # Update session ID if returned (shouldn't change but good practice)
                if "session_id" in response_data:
                    st.session_state.session_id = response_data["session_id"]
                
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
    - 🧠 **Remembers our conversation!**
    """)
    
    # Display session info
    st.markdown("## Session Info")
    st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    
        # Session management buttons
    if st.button("🔄 New Session", use_container_width=True):
        try:
            # Clear session on backend
            requests.delete(f"http://backend:8000/sessions/{st.session_state.session_id}")
        except:
            pass  # Ignore errors when clearing backend session
        
        # Generate new session ID and clear frontend history
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
