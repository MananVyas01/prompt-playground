import streamlit as st
import json
import os
import time
import difflib
from typing import Dict, List, Tuple
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
        "microsoft/DialoGPT-small"
    ]

def generate_with_timing(model_pipeline, prompt: str, max_new_tokens: int = 50) -> Tuple[str, float]:
    """Generate text with timing information"""
    start_time = time.time()
    response = generate_text(model_pipeline, prompt, max_new_tokens)
    end_time = time.time()
    generation_time = end_time - start_time
    return response, generation_time

def highlight_differences(responses: List[str], model_names: List[str]) -> str:
    """Generate HTML highlighting differences between responses"""
    if len(responses) < 2:
        return ""
    
    # Compare first two responses
    diff = difflib.unified_diff(
        responses[0].splitlines(keepends=True),
        responses[1].splitlines(keepends=True),
        fromfile=model_names[0],
        tofile=model_names[1],
        lineterm=''
    )
    
    diff_text = ''.join(diff)
    return diff_text if diff_text else "No significant differences detected."

def get_response_color(index: int) -> str:
    """Get color for response card based on index"""
    colors = ["#e8f4f8", "#f0f8e8", "#f8f0e8", "#f4e8f8", "#e8f8f4"]
    return colors[index % len(colors)]

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
    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = ["sshleifer/tiny-gpt2"]
    if 'model_responses' not in st.session_state:
        st.session_state.model_responses = {}
    if 'last_comparison_prompt' not in st.session_state:
        st.session_state.last_comparison_prompt = ""
    
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
    
    # Model Selector (Multi-select)
    selected_models = st.sidebar.multiselect(
        "🤖 Select Models to Compare",
        models,
        default=st.session_state.selected_models,
        help="Choose up to 3 models for comparison (memory limit)",
        max_selections=3
    )
    
    # Update session state
    if selected_models != st.session_state.selected_models:
        st.session_state.selected_models = selected_models
        # Clear previous responses when models change
        st.session_state.model_responses = {}
    
    # Warning if no models selected
    if not selected_models:
        st.sidebar.warning("⚠️ Please select at least one model")
        return
    
    # Show selected models info
    if len(selected_models) > 1:
        st.sidebar.info(f"📊 Comparing {len(selected_models)} models")
    
    # Show model info for selected models
    with st.sidebar.expander("🤖 Selected Models Info"):
        for model in selected_models:
            model_info = get_model_info(model)
            st.write(f"**{model}**")
            st.write(f"- Type: {model_info['type']}")
            st.write(f"- Size: {model_info['size']}")
            st.write("---")
    
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
    submit_button = st.sidebar.button("🚀 Generate Comparison", type="primary", key="generate_btn")
    
    # Regenerate Button (only show if there are previous responses)
    regenerate_button = False
    if (st.session_state.model_responses and 
        st.session_state.last_comparison_prompt and
        set(selected_models) == set(st.session_state.model_responses.keys())):
        regenerate_button = st.sidebar.button("🔄 Regenerate All", key="regenerate_btn")
    
    # Add comparison options
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Comparison Options")
    show_differences = st.sidebar.checkbox(
        "🔍 Highlight Differences", 
        value=False,
        help="Show textual differences between model responses"
    )
    show_timing = st.sidebar.checkbox(
        "⏱️ Show Generation Time", 
        value=True,
        help="Display how long each model took to generate"
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
        st.subheader("⚡ Model Comparison Results")
        
        # Handle generation for multiple models
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
                st.session_state.last_comparison_prompt = final_prompt
                
                # Show what we're generating
                st.write("**📝 Prompt for all models:**")
                st.code(final_prompt, language="text")
                
                # Initialize responses dictionary
                st.session_state.model_responses = {}
                
                # Generate responses for each model
                progress_bar = st.progress(0)
                total_models = len(selected_models)
                
                for i, model_name in enumerate(selected_models):
                    progress_bar.progress((i) / total_models)
                    
                    with st.spinner(f"Loading {model_name}..."):
                        model_pipeline = load_model(model_name)
                    
                    if model_pipeline is not None:
                        with st.spinner(f"Generating with {model_name}..."):
                            response, gen_time = generate_with_timing(
                                model_pipeline, final_prompt, max_new_tokens=50
                            )
                            st.session_state.model_responses[model_name] = {
                                'response': response,
                                'time': gen_time
                            }
                    else:
                        st.session_state.model_responses[model_name] = {
                            'response': f"❌ Failed to load {model_name}",
                            'time': 0
                        }
                
                progress_bar.progress(1.0)
                st.success(f"✅ Generated responses from {total_models} models!")
        
        # Display comparison results
        if st.session_state.model_responses:
            st.markdown("---")
            
            # Show responses in columns
            if len(st.session_state.model_responses) == 1:
                # Single model - use full width
                model_name = list(st.session_state.model_responses.keys())[0]
                response_data = st.session_state.model_responses[model_name]
                
                st.write(f"**🤖 {model_name}**")
                
                if show_timing:
                    st.caption(f"⏱️ Generation time: {response_data['time']:.2f}s")
                
                if response_data['response'].startswith("❌"):
                    st.error(response_data['response'])
                else:
                    st.success(response_data['response'])
                
            else:
                # Multiple models - use columns
                cols = st.columns(len(st.session_state.model_responses))
                
                for i, (model_name, response_data) in enumerate(st.session_state.model_responses.items()):
                    with cols[i]:
                        # Model header with color
                        bg_color = get_response_color(i)
                        st.markdown(
                            f"""<div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: #333;">🤖 {model_name}</h4>
                            </div>""", 
                            unsafe_allow_html=True
                        )
                        
                        if show_timing:
                            st.caption(f"⏱️ {response_data['time']:.2f}s")
                        
                        # Response
                        if response_data['response'].startswith("❌"):
                            st.error(response_data['response'])
                        else:
                            st.markdown(f"**Response:**")
                            st.code(response_data['response'], language="text")
                        
                        # Model info
                        model_info = get_model_info(model_name)
                        st.caption(f"📊 {model_info['type']} • {model_info['size']}")
            
            # Show differences if requested and multiple models
            if show_differences and len(st.session_state.model_responses) > 1:
                st.markdown("---")
                st.subheader("🔍 Response Differences")
                
                responses = [data['response'] for data in st.session_state.model_responses.values()]
                model_names = list(st.session_state.model_responses.keys())
                
                if len(set(responses)) == 1:
                    st.info("💡 All models generated identical responses!")
                else:
                    diff_text = highlight_differences(responses, model_names)
                    if diff_text and diff_text != "No significant differences detected.":
                        st.code(diff_text, language="diff")
                    else:
                        st.info("💡 No significant differences detected between responses.")
            
            # Comparison analytics
            if len(st.session_state.model_responses) > 1:
                st.markdown("---")
                st.subheader("📊 Comparison Analytics")
                
                # Response lengths
                lengths = {name: len(data['response']) for name, data in st.session_state.model_responses.items()}
                fastest_model = min(st.session_state.model_responses.keys(), 
                                  key=lambda x: st.session_state.model_responses[x]['time'])
                longest_response = max(lengths.keys(), key=lambda x: lengths[x])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("🏃 Fastest Model", fastest_model, 
                            f"{st.session_state.model_responses[fastest_model]['time']:.2f}s")
                with col_b:
                    st.metric("📝 Longest Response", longest_response, 
                            f"{lengths[longest_response]} chars")
            
            # Copy all responses button
            if st.button("📋 Copy All Responses", key="copy_all_responses"):
                all_responses = []
                for model_name, response_data in st.session_state.model_responses.items():
                    all_responses.append(f"=== {model_name} ===\n{response_data['response']}\n")
                
                combined_text = "\n".join(all_responses)
                if CLIPBOARD_AVAILABLE and copy_to_clipboard(combined_text):
                    st.success("✅ All responses copied to clipboard!")
                else:
                    st.info("📋 Copy to clipboard:")
                    st.code(combined_text)
        
        else:
            st.info("Select models and click 'Generate Comparison' to see results")
            
            if selected_models:
                st.write("**Selected models for comparison:**")
                for model in selected_models:
                    model_info = get_model_info(model)
                    st.write(f"• **{model}** - {model_info['type']} ({model_info['size']})")

if __name__ == "__main__":
    main()
