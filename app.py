import streamlit as st
import json
import os
import time
import difflib
from typing import Dict, List
from models.load_model import load_model, generate_text, get_model_info
from utils.prompt_formatter import format_prompt, validate_template, count_tokens_estimate

# Try to import pyperclip, but provide fallback if not available
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

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
        "microsoft/DialoGPT-small",
        "gpt2"  # Added standard GPT-2 for comparison
    ]

def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard with fallback for environments where clipboard is not available"""
    if not CLIPBOARD_AVAILABLE:
        return False
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
    if 'last_generated_responses' not in st.session_state:
        st.session_state.last_generated_responses = {}
    if 'last_models_used' not in st.session_state:
        st.session_state.last_models_used = []
    
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
    selected_models = st.sidebar.multiselect(
        "🤖 Select Models (2-3 max)",
        models,
        default=["sshleifer/tiny-gpt2"],
        max_selections=3,
        help="Choose up to 3 lightweight models for comparison"
    )
    
    # Warning if too many models selected
    if len(selected_models) > 3:
        st.sidebar.warning("⚠️ Please select max 3 models to avoid memory issues")
    elif len(selected_models) == 0:
        st.sidebar.warning("⚠️ Please select at least one model")
    
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
            if CLIPBOARD_AVAILABLE and copy_to_clipboard(template_text):
                st.sidebar.success("✅ Copied!")
            else:
                st.sidebar.info("📋 Copy to clipboard:")
                st.sidebar.code(template_text)
    
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
    
    # Regenerate Button (only show if there are previous responses)
    regenerate_button = False
    if (st.session_state.last_generated_responses and 
        set(st.session_state.last_models_used) == set(selected_models)):
        regenerate_button = st.sidebar.button("🔄 Regenerate All Responses", key="regenerate_btn")
    
    # Comparison Options
    st.sidebar.subheader("🔍 Comparison Settings")
    highlight_differences = st.sidebar.checkbox(
        "🔍 Highlight Differences",
        value=False,
        help="Show differences between model responses"
    )
    show_timing = st.sidebar.checkbox(
        "⏱️ Show Generation Time",
        value=True,
        help="Display time taken for each model"
    )
    
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
                    if CLIPBOARD_AVAILABLE and copy_to_clipboard(final_prompt):
                        st.success("✅ Final prompt copied to clipboard!")
                    else:
                        st.info("📋 Copy to clipboard:")
                        st.code(final_prompt)
    
    with col2:
        st.subheader("⚡ Model Outputs")
        
        # Show model info for selected models
        if selected_models:
            with st.expander("🤖 Selected Models Information"):
                for model in selected_models:
                    model_info = get_model_info(model)
                    st.write(f"**{model}**: {model_info['type']} ({model_info['size']})")
        
        # Handle generation
        if submit_button or regenerate_button:
            if not user_input.strip():
                st.warning("⚠️ Please enter some input text first!")
            elif not template_text.strip():
                st.warning("⚠️ Please provide a template!")
            elif not is_valid:
                st.error(f"⚠️ Template error: {error_msg}")
            elif not selected_models:
                st.warning("⚠️ Please select at least one model!")
            else:
                # Get the final prompt
                final_prompt = format_prompt(template_text, user_input.strip())
                
                # Show what we're generating
                st.write("**📝 Generating for:**")
                st.code(final_prompt, language="text")
                
                # Initialize results storage
                model_responses = {}
                generation_times = {}
                
                # Generate responses for each model
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, model_name in enumerate(selected_models):
                    status_text.text(f"Loading {model_name}...")
                    progress_bar.progress((i) / len(selected_models))
                    
                    # Load model
                    with st.spinner(f"Loading {model_name}..."):
                        model_pipeline = load_model(model_name)
                    
                    if model_pipeline is not None:
                        status_text.text(f"Generating with {model_name}...")
                        
                        # Time the generation
                        start_time = time.time()
                        with st.spinner(f"Generating with {model_name}..."):
                            generated_text = generate_text(model_pipeline, final_prompt, max_new_tokens=50)
                        end_time = time.time()
                        
                        model_responses[model_name] = generated_text
                        generation_times[model_name] = end_time - start_time
                    else:
                        model_responses[model_name] = "❌ Failed to load model"
                        generation_times[model_name] = 0
                
                progress_bar.progress(1.0)
                status_text.text("Generation complete!")
                
                # Store in session state
                st.session_state.last_generated_responses = model_responses
                st.session_state.last_models_used = selected_models
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display results side by side
                st.write("**🤖 Model Comparison:**")
                
                # Create columns for side-by-side comparison
                if len(selected_models) == 1:
                    cols = st.columns(1)
                elif len(selected_models) == 2:
                    cols = st.columns(2)
                else:
                    cols = st.columns(3)
                
                # Display each model's response
                for i, model_name in enumerate(selected_models):
                    with cols[i]:
                        model_info = get_model_info(model_name)
                        
                        # Model header with colored background
                        color = ["#FF6B6B", "#4ECDC4", "#45B7D1"][i % 3]
                        st.markdown(f"""
                        <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="color: white; margin: 0;">{model_info['type']}</h4>
                            <small style="color: white;">{model_name}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Response
                        response = model_responses.get(model_name, "No response")
                        if response.startswith("❌"):
                            st.error(response)
                        else:
                            st.success(response)
                        
                        # Timing info
                        if show_timing and model_name in generation_times:
                            timing = generation_times[model_name]
                            st.caption(f"⏱️ Generated in {timing:.2f}s")
                        
                        # Copy button for individual response
                        if st.button(f"📋 Copy", key=f"copy_{model_name.replace('/', '_')}"):
                            if CLIPBOARD_AVAILABLE and copy_to_clipboard(response):
                                st.success("✅ Copied!")
                            else:
                                st.info("📋 Copy:")
                                st.code(response)
                
                # Difference highlighting if enabled
                if highlight_differences and len(selected_models) > 1:
                    st.write("**🔍 Response Differences:**")
                    
                    # Get valid responses
                    valid_responses = {k: v for k, v in model_responses.items() 
                                     if not v.startswith("❌")}
                    
                    if len(valid_responses) >= 2:
                        models_list = list(valid_responses.keys())
                        
                        # Compare first two models
                        model1, model2 = models_list[0], models_list[1]
                        response1 = valid_responses[model1]
                        response2 = valid_responses[model2]
                        
                        # Generate diff
                        diff = list(difflib.unified_diff(
                            response1.split(), response2.split(),
                            fromfile=model1, tofile=model2, lineterm=''))
                        
                        if diff:
                            st.code('\n'.join(diff), language='diff')
                        else:
                            st.info("No significant differences found between responses")
                    else:
                        st.info("Need at least 2 valid responses to show differences")
        
        # Show last responses if available
        elif st.session_state.last_generated_responses:
            st.write("**🤖 Last Generated Responses:**")
            
            # Create columns for last responses
            last_models = st.session_state.last_models_used
            if len(last_models) == 1:
                cols = st.columns(1)
            elif len(last_models) == 2:
                cols = st.columns(2)
            else:
                cols = st.columns(3)
            
            for i, model_name in enumerate(last_models):
                with cols[i]:
                    model_info = get_model_info(model_name)
                    st.write(f"**{model_info['type']}**")
                    response = st.session_state.last_generated_responses.get(model_name, "No response")
                    if response.startswith("❌"):
                        st.error(response)
                    else:
                        st.info(response)
                    st.caption(f"Model: {model_name}")
        
        else:
            st.info("Configure your prompt and click 'Generate' to see the outputs")
            st.write("**💡 Multi-Model Comparison Features:**")
            st.write("• Select up to 3 models for side-by-side comparison")
            st.write("• View generation timing for performance analysis")  
            st.write("• Highlight differences between responses")
            st.write("• Copy individual responses to clipboard")

if __name__ == "__main__":
    main()
