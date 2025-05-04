import streamlit as st
import requests
import json
import time
from PIL import Image
import os

# Set up page configuration
st.set_page_config(
    page_title="LangChain Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4527A0;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5E35B1;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .user-bubble {
        background-color: #E3F2FD;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #2196F3;
    }
    .ai-bubble {
        background-color: #F3E5F5;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #9C27B0;
    }
    .tool-tag {
        background-color: #E8EAF6;
        color: #3F51B5;
        padding: 3px 8px;
        border-radius: 8px;
        font-size: 0.8rem;
        margin-top: 5px;
        display: inline-block;
    }
    .error-message {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
    }
    .flowchart-container {
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #4527A0;
    }
    .sidebar-subheader {
        font-size: 1.0rem;
        font-weight: bold;
        margin-top: 15px;
        color: #5E35B1;
    }
    .sidebar-text {
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    .sidebar-section {
        background-color: #F5F7FA;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:5000/api/query"

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with controls, info, and architecture flowchart
with st.sidebar:
    st.image("https://nathankjer.com/wp-content/uploads/2023/04/imageedit_3_8921363341-e1680611897170.png", width=200)

    st.markdown('<div class="sidebar-header">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-text">This chatbot is powered by LangChain, Ollama, MongoDB, and SQL to provide intelligent responses about NVIDIA.</div>',
        unsafe_allow_html=True)

    # Controls
    st.markdown('<div class="sidebar-header">Controls</div>', unsafe_allow_html=True)
    if st.button("Clear Conversation", key="clear_chat"):
        st.session_state.messages = []
        st.experimental_rerun()

    # System Architecture section with expander
    st.markdown('<div class="sidebar-header">System Architecture</div>', unsafe_allow_html=True)
    with st.expander("View System Flowchart", expanded=False):
        # Flowchart container
        st.markdown('<div>', unsafe_allow_html=True)

        # Path to your flowchart PNG file
        flowchart_path = "flow.png"  # Replace with your actual file path


        # Function to load and display the image
        def load_image(image_path):
            try:
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    st.image(image, caption="System Architecture", use_container_width=True)
                else:
                    st.error(f"Image not found: {image_path}")
                    st.info("Update the flowchart path in the code.")
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")


        # Try to load the image
        load_image(flowchart_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # Architecture explanation
        st.markdown('<div class="sidebar-subheader">How It Works</div>', unsafe_allow_html=True)
        st.markdown("""
        1. User enters a query
        2. Query sent to Flask backend
        3. LangChain analyzes and routes to appropriate tool
        4. Tool processes and generates response
        5. Response displayed to user
        """)

    # Tools info in an expander
    st.markdown('<div class="sidebar-header">Tools Available</div>', unsafe_allow_html=True)
    with st.expander("View Tools", expanded=False):
        st.markdown('<div class="sidebar-subheader">Data Sources</div>', unsafe_allow_html=True)
        st.markdown("""
        - **MongoDB**: Unstructured knowledge
        - **SQL Database**: Structured data like specs
        - **LLM**: Reasoning capabilities
        """)

        st.markdown('<div class="sidebar-subheader">Technologies</div>', unsafe_allow_html=True)
        st.markdown("""
        - **LangChain**: Orchestration framework
        - **Streamlit**: User interface
        - **Flask**: Backend API
        - **Ollama**: Local LLM
        """)

    # Tips section
    st.markdown('<div class="sidebar-header">Tips</div>', unsafe_allow_html=True)
    with st.expander("Usage Tips", expanded=False):
        st.markdown("""
        - Ask specific questions about NVIDIA products
        - Try asking for comparisons between different GPUs
        - You can inquire about historical data or recent trends
        """)

# Main app content
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown('<h1 class="main-header">LangChain Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">A chatbot powered by LangChain, Ollama, MongoDB, and SQL</p>',
                unsafe_allow_html=True)

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat history with improved styling
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-bubble"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                tool_info = f'<div class="tool-tag">🛠️ Tool: {message["tool"]}</div>' if "tool" in message else ""
                st.markdown(
                    f'<div class="ai-bubble"><b>AI:</b> {message["content"]}{tool_info}</div>',
                    unsafe_allow_html=True
                )

    # Chat input at the bottom
    prompt_input = st.chat_input("Ask something about NVIDIA...")

    if prompt_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt_input})

        # Display user message (will be added to the chat container on rerun)
        st.markdown(f'<div class="user-bubble"><b>You:</b> {prompt_input}</div>', unsafe_allow_html=True)

        # Create placeholder for assistant response
        response_placeholder = st.empty()

        # Show thinking animation
        with response_placeholder.container():
            thinking_text = "AI is thinking"
            for i in range(3):
                st.markdown(f'<div class="ai-bubble"><b>AI:</b> {thinking_text}{"." * (i + 1)}</div>',
                            unsafe_allow_html=True)
                time.sleep(0.5)
                if i < 2:  # Don't need to clear on the last iteration
                    st.empty()

        # Generate response
        try:
            # Call the Flask API
            response = requests.post(
                API_URL,
                json={"query": prompt_input},
                headers={"Content-Type": "application/json"},
                timeout=30  # Add timeout
            )

            if response.status_code == 200:
                data = response.json()
                final_response = data["response"]
                tool_used = data["tool_used"]

                # Update placeholder with real response
                with response_placeholder.container():
                    tool_info = f'<div class="tool-tag">🛠️ Tool: {tool_used}</div>'
                    st.markdown(
                        f'<div class="ai-bubble"><b>AI:</b> {final_response}{tool_info}</div>',
                        unsafe_allow_html=True
                    )

                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_response,
                    "tool": tool_used
                })
            else:
                error_msg = f"The server returned an error (Status: {response.status_code}). Please try again or contact support if the problem persists."
                with response_placeholder.container():
                    st.markdown(f'<div class="ai-bubble"><b>AI:</b> <div class="error-message">{error_msg}</div></div>',
                                unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "tool": "Error"
                })
        except requests.exceptions.Timeout:
            error_msg = "The request timed out. The server might be experiencing heavy load. Please try again."
            with response_placeholder.container():
                st.markdown(f'<div class="ai-bubble"><b>AI:</b> <div class="error-message">{error_msg}</div></div>',
                            unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "tool": "Timeout"
            })
        except Exception as e:
            error_msg = f"Unable to connect to the backend server. Please check if the server is running or try again later."
            with response_placeholder.container():
                st.markdown(f'<div class="ai-bubble"><b>AI:</b> <div class="error-message">{error_msg}</div></div>',
                            unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "tool": "Error"
            })