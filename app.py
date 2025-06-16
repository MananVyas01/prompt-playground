import streamlit as st
import json
import os
import pyperclip
from typing import Dict, List
from models.load_model import load_model, generate_text, get_model_info
from utils.prompt_formatter import format_prompt, validate_template, count_tokens_estimate

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
        "microsoft/DialoGPT-small"
    ]

def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return True
    except:
        return False

def main():
    # Header
    st.title("🧠 Prompt Playground")
    st.markdown("*An interactive app to test different types of prompts with small, CPU-only open-source language models*")
    
    # Load data
    prompt_types = load_prompt_types()
    models = load_models()
    
    # Initialize session state
    if 'current_prompt_type' not in st.session_state:
        st.session_state.current_prompt_type = list(prompt_types.keys())[0] if prompt_types else ""
    if 'template_text' not in st.session_state:
        st.session_state.template_text = ""
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'last_generated_response' not in st.session_state:
        st.session_state.last_generated_response = ""
    if 'last_model_used' not in st.session_state:
        st.session_state.last_model_used = ""
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Prompt Type Selector
    if prompt_types:
        prompt_type_names = list(prompt_types.keys())
        selected_prompt_type = st.sidebar.selectbox(
            "📝 Prompt Type",
            prompt_type_names,
            index=prompt_type_names.index(st.session_state.current_prompt_type) if st.session_state.current_prompt_type in prompt_type_names else 0,
            help="Select the type of prompt you want to test",
            key="prompt_type_selector"
        )
        
        # Update session state and auto-fill template when prompt type changes
        if selected_prompt_type != st.session_state.current_prompt_type:
            st.session_state.current_prompt_type = selected_prompt_type
            if selected_prompt_type in prompt_types:
                st.session_state.template_text = prompt_types[selected_prompt_type].get("template", "")
                st.rerun()
    else:
        st.sidebar.error("No prompt types available")
        return
    
    # Model Selector
    selected_model = st.sidebar.selectbox(
        "🤖 Model",
        models,
        help="Choose a lightweight model optimized for CPU inference"
    )
    
    # Sidebar spacing
    st.sidebar.markdown("---")
    
    # Template Editor in Sidebar
    st.sidebar.subheader("📝 Template Editor")
    
    # Auto-fill template if needed
    if not st.session_state.template_text and selected_prompt_type in prompt_types:
        st.session_state.template_text = prompt_types[selected_prompt_type].get("template", "")
    
    # Template text area
    template_text = st.sidebar.text_area(
        "Edit Template:",
        value=st.session_state.template_text,
        height=150,
        help="Edit the prompt template. Use {input} as placeholder for user input.",
        key="template_editor"
    )
    
    # Update session state
    st.session_state.template_text = template_text
    
    # Template validation
    is_valid, error_msg = validate_template(template_text)
    if not is_valid:
        st.sidebar.error(f"⚠️ {error_msg}")
    
    # Quick template actions
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Reset", help="Reset to original template", key="reset_template"):
            if selected_prompt_type in prompt_types:
                st.session_state.template_text = prompt_types[selected_prompt_type].get("template", "")
                st.rerun()
    
    with col2:
        if st.button("📋 Copy", help="Copy template to clipboard", key="copy_template"):
            if copy_to_clipboard(template_text):
                st.sidebar.success("✅ Copied!")
            else:
                st.sidebar.error("❌ Copy failed")
    
    # User Input in Sidebar
    st.sidebar.subheader("✍️ User Input")
    
    # Get placeholder text
    placeholder_text = ""
    if selected_prompt_type in prompt_types:
        placeholder_text = prompt_types[selected_prompt_type].get("input_placeholder", "Enter your input here...")
    
    user_input = st.sidebar.text_area(
        "Your Input:",
        value=st.session_state.user_input,
        height=100,
        placeholder=placeholder_text,
        help="This will replace {input} in the template",
        key="user_input_field"
    )
    
    # Update session state
    st.session_state.user_input = user_input
    
    # Submit Button
    submit_button = st.sidebar.button("🚀 Generate", type="primary", key="generate_btn")
    
    # Regenerate Button (only show if there's a previous response)
    regenerate_button = False
    if st.session_state.last_generated_response and st.session_state.last_model_used == selected_model:
        regenerate_button = st.sidebar.button("🔄 Regenerate Response", key="regenerate_btn")
    
    # Main Panel
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Prompt Template & Preview")
        
        if selected_prompt_type in prompt_types:
            prompt_data = prompt_types[selected_prompt_type]
            
            # Show description in expander
            with st.expander("ℹ️ About this prompt type", expanded=False):
                st.write(prompt_data.get("description", "No description available"))
                
                # Show input guidance
                if "input_placeholder" in prompt_data:
                    st.write("**Input Guidance:**")
                    st.write(f"💡 {prompt_data['input_placeholder']}")
            
            # Show current template
            st.write("**Current Template:**")
            st.code(template_text, language="text")
            
            # Show final prompt preview if user has input
            if user_input.strip() and template_text:
                st.write("**� Final Prompt Preview:**")
                final_prompt = format_prompt(template_text, user_input.strip())
                st.code(final_prompt, language="text")
                
                # Token estimation
                token_count = count_tokens_estimate(final_prompt)
                if token_count > 400:
                    st.warning(f"⚠️ Long prompt ({token_count} tokens). May be truncated.")
                else:
                    st.info(f"📊 Estimated tokens: {token_count}")
                
                # Copy final prompt button
                if st.button("📋 Copy Final Prompt", key="copy_final_prompt"):
                    if copy_to_clipboard(final_prompt):
                        st.success("✅ Final prompt copied to clipboard!")
                    else:
                        st.error("❌ Failed to copy to clipboard")
    
    with col2:
        st.subheader("⚡ Model Output")
        
        # Show model info
        model_info = get_model_info(selected_model)
        with st.expander("🤖 Model Information"):
            st.write(f"**Type:** {model_info['type']}")
            st.write(f"**Size:** {model_info['size']}")
            st.write(f"**Task:** {model_info['task']}")
            st.write(f"**Description:** {model_info['description']}")
        
        # Handle generation
        if submit_button or regenerate_button:
            if not user_input.strip():
                st.warning("⚠️ Please enter some input text first!")
            elif not template_text.strip():
                st.warning("⚠️ Please provide a template!")
            elif not is_valid:
                st.error(f"⚠️ Template error: {error_msg}")
            else:
                # Get the final prompt
                final_prompt = format_prompt(template_text, user_input.strip())
                
                # Show what we're generating
                st.write("**📝 Generating for:**")
                st.code(final_prompt, language="text")
                
                # Load model and generate text
                with st.spinner(f"Loading {selected_model}..."):
                    model_pipeline = load_model(selected_model)
                
                if model_pipeline is not None:
                    with st.spinner("Generating response..."):
                        generated_text = generate_text(model_pipeline, final_prompt, max_new_tokens=50)
                    
                    # Display results
                    st.write("**🤖 Generated Response:**")
                    if generated_text.startswith("❌"):
                        st.error(generated_text)
                    else:
                        st.success(generated_text)
                        
                        # Store in session state for regeneration
                        st.session_state.last_generated_response = generated_text
                        st.session_state.last_model_used = selected_model
                        
                        # Copy response button
                        if st.button("📋 Copy Response", key="copy_response"):
                            if copy_to_clipboard(generated_text):
                                st.success("✅ Response copied to clipboard!")
                            else:
                                st.error("❌ Failed to copy to clipboard")
                        
                        # Show generation info
                        st.caption(f"Generated with {selected_model} • Max tokens: 50 • Temperature: 0.7")
                else:
                    st.error("❌ Failed to load the selected model. Please try a different model.")
        
        # Show last response if available
        elif st.session_state.last_generated_response:
            st.write("**🤖 Last Generated Response:**")
            st.info(st.session_state.last_generated_response)
            st.caption(f"Generated with {st.session_state.last_model_used}")
        
        else:
            st.info("Configure your prompt and click 'Generate' to see the output")

if __name__ == "__main__":
    main()
