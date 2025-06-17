import streamlit as st
import json
import os
import time
import difflib
import base64
from datetime import datetime
from typing import Dict, List
from models.load_model import load_model, generate_text, get_model_info
from utils.prompt_formatter import (
    format_prompt,
    validate_template,
    count_tokens_estimate,
)
from utils.safety import safe_format_prompt, filter_output, validate_input

# Try to import pyperclip, but provide fallback if not available
try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Prompt Engineering Studio",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_logo():
    """Load and display logo if available"""
    try:
        # Try SVG first
        if os.path.exists("assets/logo.svg"):
            with open("assets/logo.svg", "r") as f:
                svg_content = f.read()
            return svg_content, "svg"
        # Fallback to PNG
        elif os.path.exists("assets/logo.png"):
            with open("assets/logo.png", "rb") as f:
                png_data = f.read()
            return base64.b64encode(png_data).decode(), "png"
    except Exception:
        pass
    return None, None


def initialize_session_state():
    """Initialize session state variables"""
    if "session_memory" not in st.session_state:
        st.session_state.session_memory = []
    if "remember_session" not in st.session_state:
        st.session_state.remember_session = False
    if "dark_theme" not in st.session_state:
        st.session_state.dark_theme = False
    if "last_generated_responses" not in st.session_state:
        st.session_state.last_generated_responses = {}
    if "last_models_used" not in st.session_state:
        st.session_state.last_models_used = []
    if "generation_times" not in st.session_state:
        st.session_state.generation_times = {}


def save_to_session_memory(
    prompt_type, user_input, final_prompt, models, responses, times
):
    """Save current session to memory"""
    if st.session_state.remember_session:
        session_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt_type": prompt_type,
            "user_input": user_input,
            "final_prompt": final_prompt,
            "models": models,
            "responses": responses,
            "generation_times": times,
        }
        st.session_state.session_memory.append(session_entry)
        # Keep only last 10 sessions to avoid memory issues
        if len(st.session_state.session_memory) > 10:
            st.session_state.session_memory = st.session_state.session_memory[-10:]


def create_download_content(
    prompt_type, user_input, final_prompt, models, responses, times, format_type="txt"
):
    """Create downloadable content in specified format"""
    if format_type == "txt":
        content = f"""PROMPT PLAYGROUND EXPORT
{'='*50}

Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Prompt Type: {prompt_type}
User Input: {user_input}

Final Prompt:
{'-'*20}
{final_prompt}

Model Responses:
{'-'*20}
"""
        for model in models:
            response = responses.get(model, "No response")
            gen_time = times.get(model, 0)
            content += f"\nModel: {model}\n"
            content += f"Generation Time: {gen_time:.2f}s\n"
            content += f"Response: {response}\n"
            content += "-" * 30 + "\n"

    elif format_type == "md":
        content = f"""# 🧠 Prompt Playground Export

**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Prompt Type:** {prompt_type}  
**User Input:** {user_input}

## Final Prompt
```
{final_prompt}
```

## Model Responses
"""
        for model in models:
            response = responses.get(model, "No response")
            gen_time = times.get(model, 0)
            content += f"\n### {model}\n"
            content += f"**Generation Time:** {gen_time:.2f}s\n\n"
            content += f"```\n{response}\n```\n"

    return content


@st.cache_resource
def load_prompt_types() -> Dict:
    """Load prompt types from JSON file"""
    try:
        with open("prompt_types.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("prompt_types.json file not found!")
        return {}


def load_models() -> List[str]:
    """Return list of available prompt optimization tools and models"""
    return [
        "Prompt Refiner (🔧 AI-Powered Optimization)",      # Main prompt refiner
        "Prompt Analyzer (📊 Structure Analysis)",          # Analyzes prompt structure
        "Few-Shot Generator (📝 Example Creator)",           # Creates few-shot examples
        "Chain-of-Thought Builder (🧠 Reasoning Guide)",     # Builds CoT prompts
        "--- VALIDATION MODELS ---",                        # Separator
        "google/flan-t5-small (🤖 Instruction-Tuned)",     # For testing refined prompts
        "microsoft/DialoGPT-small (💬 Conversational)",     # Dialogue testing
        "distilgpt2 (⚠️ Baseline Comparison)",              # Baseline for comparison
        "--- ENTERPRISE MODELS (Optional) ---",             # Future expansion
        # "gpt-3.5-turbo-instruct (🏢 Enterprise API)",     # API-based testing
        # "claude-instant (⚡ Professional API)",           # Alternative API testing
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


def get_actual_model_name(display_name: str) -> str:
    """Convert display name to actual model name for loading"""
    model_mapping = {
        "Prompt Refiner (🔧 AI-Powered Optimization)": "prompt_refiner",
        "Prompt Analyzer (📊 Structure Analysis)": "prompt_analyzer", 
        "Few-Shot Generator (📝 Example Creator)": "few_shot_generator",
        "Chain-of-Thought Builder (🧠 Reasoning Guide)": "cot_builder",
        "google/flan-t5-small (🤖 Instruction-Tuned)": "google/flan-t5-small",
        "microsoft/DialoGPT-small (💬 Conversational)": "microsoft/DialoGPT-small",
        "distilgpt2 (⚠️ Baseline Comparison)": "distilgpt2",
        # Separators are ignored
        "--- VALIDATION MODELS ---": None,
        "--- ENTERPRISE MODELS (Optional) ---": None,
        # Other models use their display name as actual name
    }
    actual_name = model_mapping.get(display_name, display_name)
    return actual_name if actual_name is not None else display_name


def is_unsafe_model(model_name: str) -> bool:
    """Check if a model is marked as potentially unsafe"""
    return "⚠️" in model_name


def main():
    # Initialize session state
    initialize_session_state()

    # Header with logo
    logo_content, logo_type = load_logo()
    if logo_content and logo_type == "svg":
        st.markdown(
            f'<div style="text-align: center;">{logo_content}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
    elif logo_content and logo_type == "png":
        st.markdown(
            f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_content}" width="200"></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.title("🔧 Prompt Engineering Studio")

    st.markdown(
        "*Professional prompt engineering and optimization platform for AI/LLM interactions*"
    )

    # Load data
    prompt_types = load_prompt_types()
    models = load_models()

    # Initialize additional session state
    if "current_prompt_type" not in st.session_state:
        st.session_state.current_prompt_type = (
            list(prompt_types.keys())[0] if prompt_types else ""
        )
    if "template_text" not in st.session_state:
        st.session_state.template_text = ""
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Sidebar
    st.sidebar.header("⚙️ Configuration")

    # Theme Toggle
    theme_col1, theme_col2 = st.sidebar.columns([1, 2])
    with theme_col1:
        st.markdown("🎨")
    with theme_col2:
        dark_theme = st.checkbox(
            "Dark Theme", value=st.session_state.dark_theme, key="theme_toggle"
        )
        if dark_theme != st.session_state.dark_theme:
            st.session_state.dark_theme = dark_theme
            st.info("🔄 Theme change will apply on next refresh")

    # Session Memory Toggle
    memory_col1, memory_col2 = st.sidebar.columns([1, 2])
    with memory_col1:
        st.markdown("💾")
    with memory_col2:
        st.session_state.remember_session = st.checkbox(
            "Remember my session",
            value=st.session_state.remember_session,
            help="Save prompts and responses in session memory",
        )

    st.sidebar.markdown("---")

    # Prompt Type Selector
    if prompt_types:
        prompt_type_names = list(prompt_types.keys())
        selected_prompt_type = st.sidebar.selectbox(
            "📝 Prompt Type",
            prompt_type_names,
            index=(
                prompt_type_names.index(st.session_state.current_prompt_type)
                if st.session_state.current_prompt_type in prompt_type_names
                else 0
            ),
            help="Select the type of prompt you want to test",
            key="prompt_type_selector",
        )

        # Update session state and auto-fill template when prompt type changes
        if selected_prompt_type != st.session_state.current_prompt_type:
            st.session_state.current_prompt_type = selected_prompt_type
            if selected_prompt_type in prompt_types:
                st.session_state.template_text = prompt_types[selected_prompt_type].get(
                    "template", ""
                )
                st.rerun()
    else:
        st.sidebar.error("No prompt types available")
        return

    # Filter out separator lines for the multiselect
    selectable_models = [model for model in models if not model.startswith("---")]
    
    # Prompt Engineering Tools Selector
    selected_models = st.sidebar.multiselect(
        "🔧 Select Prompt Engineering Tools",
        selectable_models,
        default=[
            "Prompt Refiner (🔧 AI-Powered Optimization)"
        ],  # Default to prompt refiner
        max_selections=3,
        help="Choose up to 3 prompt engineering tools and validation models",
    )

    # Warning if too many tools selected
    if len(selected_models) > 3:
        st.sidebar.warning("⚠️ Please select max 3 tools to avoid processing conflicts")
    elif len(selected_models) == 0:
        st.sidebar.warning("⚠️ Please select at least one prompt engineering tool")

    # Safety warnings for unsafe models
    unsafe_models = [model for model in selected_models if is_unsafe_model(model)]
    if unsafe_models:
        st.sidebar.warning(
            f"⚠️ **Safety Notice**: You selected unfiltered model(s): {', '.join(unsafe_models)}. "
            "Output may contain inappropriate or NSFW content."
        )

    # Prompt Engineering Tools info
    refiner_tools = [model for model in selected_models if any(tool in model for tool in ["Refiner", "Analyzer", "Generator", "Builder"])]
    if refiner_tools:
        st.sidebar.info(
            "🔧 **Professional Mode**: You are using AI-powered prompt engineering tools for optimization and analysis."
        )

    # Sidebar spacing
    st.sidebar.markdown("---")

    # Template Editor in Sidebar
    st.sidebar.subheader("📝 Template Editor")

    # Auto-fill template if needed
    if not st.session_state.template_text and selected_prompt_type in prompt_types:
        st.session_state.template_text = prompt_types[selected_prompt_type].get(
            "template", ""
        )

    # Template text area
    template_text = st.sidebar.text_area(
        "Edit Template:",
        value=st.session_state.template_text,
        height=150,
        help="Edit the prompt template. Use {input} as placeholder for user input.",
        key="template_editor",
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
        if st.button(
            "🔄 Reset", help="Reset to original template", key="reset_template"
        ):
            if selected_prompt_type in prompt_types:
                st.session_state.template_text = prompt_types[selected_prompt_type].get(
                    "template", ""
                )
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
        placeholder_text = prompt_types[selected_prompt_type].get(
            "input_placeholder", "Enter your input here..."
        )

    user_input = st.sidebar.text_area(
        "Your Input:",
        value=st.session_state.user_input,
        height=100,
        placeholder=placeholder_text,
        help="This will replace {input} in the template",
        key="user_input_field",
    )

    # Update session state
    st.session_state.user_input = user_input

    # Input validation
    validation_message, is_valid_input = validate_input(user_input)
    if validation_message and not is_valid_input:
        st.sidebar.error(validation_message)
    elif validation_message and is_valid_input:
        st.sidebar.info(validation_message)

    # Process Button
    submit_button = st.sidebar.button("� Optimize & Analyze", type="primary", key="process_btn")

    # Regenerate Button (only show if there are previous responses)
    regenerate_button = False
    if st.session_state.last_generated_responses and set(
        st.session_state.last_models_used
    ) == set(selected_models):
        regenerate_button = st.sidebar.button(
            "🔄 Re-process with Same Tools", key="regenerate_btn"
        )

    # Comparison Options
    st.sidebar.subheader("🔍 Comparison Settings")
    highlight_differences = st.sidebar.checkbox(
        "🔍 Highlight Differences",
        value=False,
        help="Show differences between model responses",
    )
    show_timing = st.sidebar.checkbox(
        "⏱️ Show Generation Time", value=True, help="Display time taken for each model"
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

        st.divider()

        # Show current template
        st.write("**Current Template:**")
        st.code(template_text, language="text")

        # Show final prompt preview if user has input
        if user_input.strip() and template_text:
            st.write("**🔍 Final Prompt Preview:**")
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
        st.subheader("🔧 Prompt Engineering Results")

        # Show model info for selected models
        if selected_models:
            with st.expander("🤖 Selected Models Information"):
                for model in selected_models:
                    model_info = get_model_info(model)
                    st.write(
                        f"**{model}**: {model_info['type']} ({model_info['size']})"
                    )

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
            elif not is_valid_input:
                st.error("⚠️ Please fix input validation issues before generating!")
            else:
                # Create safe prompt - use safe formatting for better control
                raw_prompt = format_prompt(template_text, user_input.strip())
                final_prompt = safe_format_prompt(raw_prompt)

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
                    # Get the actual model name for loading
                    actual_model_name = get_actual_model_name(model_name)
                    status_text.text(f"Loading {actual_model_name}...")
                    progress_bar.progress((i) / len(selected_models))

                    # Load model
                    with st.spinner(f"Loading {actual_model_name}..."):
                        model_pipeline = load_model(actual_model_name)

                    if model_pipeline is not None:
                        status_text.text(f"Generating with {actual_model_name}...")

                        # Time the generation
                        start_time = time.time()
                        with st.spinner(f"Processing with {actual_model_name}..."):
                            # Handle prompt engineering tools
                            if actual_model_name in ["prompt_refiner", "prompt_analyzer", "few_shot_generator", "cot_builder", "fakegpt"]:
                                raw_generated_text = model_pipeline(final_prompt)
                            else:
                                raw_generated_text = generate_text(
                                    model_pipeline, final_prompt, max_new_tokens=50
                                )
                        end_time = time.time()

                        # Apply safety filtering (skip for prompt engineering tools)
                        if actual_model_name in ["prompt_refiner", "prompt_analyzer", "few_shot_generator", "cot_builder", "fakegpt"]:
                            filtered_text = raw_generated_text
                            was_filtered = False
                        else:
                            filtered_text, was_filtered = filter_output(raw_generated_text)

                        # Store the result
                        model_responses[model_name] = filtered_text
                        generation_times[model_name] = end_time - start_time

                        # Log if content was filtered (for debugging)
                        if was_filtered:
                            print(f"Content filtered for model {model_name}")
                    else:
                        model_responses[model_name] = "❌ Failed to load model"
                        generation_times[model_name] = 0

                progress_bar.progress(1.0)
                status_text.text("Generation complete!")

                # Store in session state
                st.session_state.last_generated_responses = model_responses
                st.session_state.last_models_used = selected_models
                st.session_state.generation_times = generation_times

                # Save to session memory if enabled
                save_to_session_memory(
                    selected_prompt_type,
                    user_input,
                    final_prompt,
                    selected_models,
                    model_responses,
                    generation_times,
                )

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                # Display results side by side
                st.write("**🔧 Prompt Engineering Analysis:**")

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
                        st.markdown(
                            f"""
                        <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="color: white; margin: 0;">{model_info['type']}</h4>
                            <small style="color: white;">{model_name}</small>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

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
                        if st.button(
                            f"📋 Copy", key=f"copy_{model_name.replace('/', '_')}"
                        ):
                            if CLIPBOARD_AVAILABLE and copy_to_clipboard(response):
                                st.success("✅ Copied!")
                            else:
                                st.info("📋 Copy:")
                                st.code(response)

                # Difference highlighting if enabled
                if highlight_differences and len(selected_models) > 1:
                    st.write("**🔍 Response Differences:**")

                    # Get valid responses
                    valid_responses = {
                        k: v
                        for k, v in model_responses.items()
                        if not v.startswith("❌")
                    }

                    if len(valid_responses) >= 2:
                        models_list = list(valid_responses.keys())

                        # Compare first two models
                        model1, model2 = models_list[0], models_list[1]
                        response1 = valid_responses[model1]
                        response2 = valid_responses[model2]

                        # Generate diff
                        diff = list(
                            difflib.unified_diff(
                                response1.split(),
                                response2.split(),
                                fromfile=model1,
                                tofile=model2,
                                lineterm="",
                            )
                        )

                        if diff:
                            st.code("\n".join(diff), language="diff")
                        else:
                            st.info(
                                "No significant differences found between responses"
                            )
                    else:
                        st.info("Need at least 2 valid responses to show differences")

                # Export Section
                st.markdown("---")
                st.write("**📥 Export Results:**")
                export_col1, export_col2 = st.columns(2)

                with export_col1:
                    # Create download content
                    txt_content = create_download_content(
                        selected_prompt_type,
                        user_input,
                        final_prompt,
                        selected_models,
                        model_responses,
                        generation_times,
                        "txt",
                    )
                    st.download_button(
                        label="📄 Download as TXT",
                        data=txt_content,
                        file_name=f"prompt_playground_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        on_click=lambda: st.toast("📄 TXT export ready!", icon="✅"),
                    )

                with export_col2:
                    md_content = create_download_content(
                        selected_prompt_type,
                        user_input,
                        final_prompt,
                        selected_models,
                        model_responses,
                        generation_times,
                        "md",
                    )
                    st.download_button(
                        label="📝 Download as Markdown",
                        data=md_content,
                        file_name=f"prompt_playground_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        on_click=lambda: st.toast(
                            "📝 Markdown export ready!", icon="✅"
                        ),
                    )

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
                    response = st.session_state.last_generated_responses.get(
                        model_name, "No response"
                    )
                    if response.startswith("❌"):
                        st.error(response)
                    else:
                        st.info(response)
                    st.caption(f"Model: {model_name}")

            # Export last responses
            if st.session_state.last_generated_responses:
                st.markdown("---")
                st.write("**📥 Export Last Results:**")
                export_col1, export_col2 = st.columns(2)

                with export_col1:
                    txt_content = create_download_content(
                        st.session_state.current_prompt_type,
                        st.session_state.user_input,
                        st.session_state.template_text,
                        st.session_state.last_models_used,
                        st.session_state.last_generated_responses,
                        st.session_state.generation_times,
                        "txt",
                    )
                    st.download_button(
                        label="📄 Download as TXT",
                        data=txt_content,
                        file_name=f"prompt_playground_last_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                    )

                with export_col2:
                    md_content = create_download_content(
                        st.session_state.current_prompt_type,
                        st.session_state.user_input,
                        st.session_state.template_text,
                        st.session_state.last_models_used,
                        st.session_state.last_generated_responses,
                        st.session_state.generation_times,
                        "md",
                    )
                    st.download_button(
                        label="📝 Download as Markdown",
                        data=md_content,
                        file_name=f"prompt_playground_last_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                    )

        # Session Memory Display
        if st.session_state.remember_session and st.session_state.session_memory:
            st.markdown("---")
            st.write("**💾 Session Memory:**")

            with st.expander(
                f"📚 View Previous Sessions ({len(st.session_state.session_memory)})"
            ):
                for i, session in enumerate(reversed(st.session_state.session_memory)):
                    st.write(
                        f"**Session {len(st.session_state.session_memory) - i}** - {session['timestamp']}"
                    )
                    st.write(f"📝 Prompt Type: {session['prompt_type']}")
                    st.write(f"💬 Input: {session['user_input'][:100]}...")

                    # Show models and response previews
                    for model in session["models"]:
                        response = session["responses"].get(model, "No response")
                        time_taken = session["generation_times"].get(model, 0)
                        st.write(
                            f"🤖 {model}: {response[:50]}... (⏱️ {time_taken:.2f}s)"
                        )

                    if i < len(st.session_state.session_memory) - 1:
                        st.markdown("---")

                # Clear session memory button
                if st.button("🗑️ Clear Session Memory"):
                    st.session_state.session_memory = []
                    st.rerun()

        else:
            st.info("Configure your prompt and click 'Generate' to see the outputs")
            st.write("**💡 Multi-Model Comparison Features:**")
            st.write("• Select up to 3 models for side-by-side comparison")
            st.write("• View generation timing for performance analysis")
            st.write("• Highlight differences between responses")
            st.write("• Copy individual responses to clipboard")


if __name__ == "__main__":
    main()
