import streamlit as st
import json
import os
from typing import Dict, List
from models.load_model import load_model, generate_text, get_model_info

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
                # Get the final prompt
                if selected_prompt_type in prompt_types:
                    prompt_data = prompt_types[selected_prompt_type]
                    final_prompt = prompt_data.get("template", "").replace("{input}", user_input)
                else:
                    final_prompt = user_input
                
                # Show model info
                model_info = get_model_info(selected_model)
                with st.expander("🤖 Model Information"):
                    st.write(f"**Type:** {model_info['type']}")
                    st.write(f"**Size:** {model_info['size']}")
                    st.write(f"**Task:** {model_info['task']}")
                    st.write(f"**Description:** {model_info['description']}")
                
                # Load model and generate text
                with st.spinner(f"Loading {selected_model}..."):
                    model_pipeline = load_model(selected_model)
                
                if model_pipeline is not None:
                    with st.spinner("Generating response..."):
                        generated_text = generate_text(model_pipeline, final_prompt, max_new_tokens=50)
                    
                    # Display results
                    st.markdown("**📝 Input Prompt:**")
                    st.code(final_prompt, language="text")
                    
                    st.markdown("**🤖 Generated Response:**")
                    if generated_text.startswith("❌"):
                        st.error(generated_text)
                    else:
                        st.success(generated_text)
                        
                        # Show generation info
                        st.caption(f"Generated with {selected_model} • Max tokens: 50 • Temperature: 0.7")
                else:
                    st.error("❌ Failed to load the selected model. Please try a different model.")
        else:
            st.info("Configure your prompt and click 'Generate' to see the output")
            
            # Show model preview when not generating
            model_info = get_model_info(selected_model)
            with st.expander("🤖 Selected Model Info"):
                st.write(f"**Model:** {selected_model}")
                st.write(f"**Type:** {model_info['type']}")
                st.write(f"**Size:** {model_info['size']}")
                st.write(f"**Description:** {model_info['description']}")

if __name__ == "__main__":
    main()
