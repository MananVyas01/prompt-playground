import streamlit as st
import json
import os
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Prompt Playground",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_prompt_types() -> Dict:
    """Load prompt types from JSON file"""
    try:
        with open('prompt_types.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("prompt_types.json file not found!")
        return {}

def load_models() -> List[str]:
    """Return list of available models"""
    return [
        "sshleifer/tiny-gpt2",
        "distilgpt2", 
        "google/flan-t5-small"
    ]

def main():
    # Header
    st.title("🧠 Prompt Playground")
    st.markdown("*An interactive app to test different types of prompts with small, CPU-only open-source language models*")
    
    # Load data
    prompt_types = load_prompt_types()
    models = load_models()
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Prompt Type Selector
    if prompt_types:
        prompt_type_names = list(prompt_types.keys())
        selected_prompt_type = st.sidebar.selectbox(
            "Prompt Type",
            prompt_type_names,
            help="Select the type of prompt you want to test"
        )
    else:
        st.sidebar.error("No prompt types available")
        return
    
    # Model Selector
    selected_model = st.sidebar.selectbox(
        "Model",
        models,
        help="Choose a lightweight model optimized for CPU inference"
    )
    
    # Prompt Input
    st.sidebar.subheader("📝 Prompt Input")
    user_input = st.sidebar.text_area(
        "Enter your prompt input:",
        height=100,
        placeholder="Type your input here..."
    )
    
    # Submit Button
    submit_button = st.sidebar.button("🚀 Generate", type="primary")
    
    # Main Panel
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Prompt Template")
        
        if selected_prompt_type in prompt_types:
            prompt_data = prompt_types[selected_prompt_type]
            
            # Show template
            st.code(prompt_data.get("template", ""), language="text")
            
            # Show description in expander
            with st.expander("ℹ️ About this prompt type"):
                st.write(prompt_data.get("description", "No description available"))
            
            # Show final prompt if user has input
            if user_input.strip():
                st.subheader("🔄 Final Prompt")
                final_prompt = prompt_data.get("template", "").replace("{input}", user_input)
                st.code(final_prompt, language="text")
    
    with col2:
        st.subheader("⚡ Model Output")
        
        if submit_button:
            if not user_input.strip():
                st.warning("Please enter some input text first!")
            else:
                # Placeholder for model output (to be implemented later)
                with st.spinner("Generating response..."):
                    st.info("🔧 Model inference will be implemented in the next stage!")
                    
                    # Show what would be generated
                    st.markdown("**Selected Model:** " + selected_model)
                    st.markdown("**Prompt Type:** " + selected_prompt_type)
                    
                    # Placeholder response
                    st.markdown("**Generated Response:**")
                    st.code("This is where the model output will appear...", language="text")
        else:
            st.info("Configure your prompt and click 'Generate' to see the output")

if __name__ == "__main__":
    main()
