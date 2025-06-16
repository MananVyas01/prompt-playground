# 🧠 Prompt Playground

A lightweight, Streamlit-based prompt engineering playground using Hugging Face models. Explore, test, and compare different prompt types like zero-shot, few-shot, and instruction prompts with small CPU-optimized language models.

## ✨ Features

- **Interactive UI**: Clean Streamlit interface with logo and customizable themes
- **Multiple Prompt Types**: Pre-configured templates for different prompting strategies
- **Live Model Inference**: Real-time text generation with Hugging Face models
- **Multi-Model Comparison**: Side-by-side comparison of up to 3 models
- **Smart Template Engine**: Auto-fill templates with validation and editing
- **Performance Timing**: Generation time analysis for each model
- **Response Differences**: Highlight textual differences between model outputs
- **Export Functionality**: Download prompts and responses as TXT or Markdown files
- **Session Memory**: Remember previous prompts and responses within the session
- **Theme Switching**: Toggle between light and dark themes
- **CPU-Optimized Models**: Works with lightweight models that run efficiently on Streamlit Cloud
- **Real-time Testing**: Instant feedback on different prompt formulations
- **Model Information**: Detailed info about each available model

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📋 Available Prompt Types

- **Instruction**: Direct instruction-following format
- **Zero-shot**: No examples, relies on model's training knowledge  
- **Few-shot**: Includes examples to guide the response
- **Chain-of-Thought**: Encourages step-by-step reasoning
- **Role-Playing**: Assigns specific personas to the model

## 🤖 Supported Models

- `sshleifer/tiny-gpt2` - Ultra-lightweight GPT-2 variant
- `distilgpt2` - Distilled version of GPT-2
- `microsoft/DialoGPT-small` - Small conversational AI model
- `gpt2` - Standard GPT-2 model for comparison

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── assets/               
│   ├── logo.svg          # App logo (SVG format)
│   └── logo.png          # App logo fallback (placeholder)
├── models/               
│   ├── __init__.py       # Models package initialization
│   └── load_model.py     # Model loading and inference utilities
├── utils/               
│   ├── __init__.py       # Utils package initialization
│   └── prompt_formatter.py # Prompt formatting and validation utilities
├── prompt_types.json      # Prompt templates and descriptions
├── requirements.txt       # Python dependencies
├── .streamlit/           
│   └── config.toml       # Streamlit configuration with theme support
└── README.md            # This file
```

## 🎨 Advanced Features

### 📥 Export Functionality
- Download prompts and model responses as TXT or Markdown files
- Includes timestamps, prompt types, model information, and generation times
- Available for current session and previous results

### 💾 Session Memory
- Enable "Remember my session" to store up to 10 previous prompt sessions
- View session history with expandable details
- Clear session memory when needed

### 🎨 Theme Support
- Toggle between light and dark themes
- Theme changes apply on next app refresh
- Configurable via `.streamlit/config.toml`

### 🖼️ Logo & Branding
- Custom logo support (place `logo.svg` or `logo.png` in `assets/` folder)
- Fallback to text-based header if no logo found

## 🎯 Roadmap

- [x] Stage 1: ✅ Initialize Project & UI Skeleton 
- [x] Stage 2: ✅ Add model inference capabilities
- [x] Stage 3: ✅ Prompt Template Autofill Engine + Smart UI
- [x] Stage 4: ✅ Multi-Model Response Comparison
- [x] Stage 5: ✅ UI Polish, Export Options & Session Memory

### 🚀 Future Enhancements
- [ ] Prompt optimization suggestions
- [ ] Model performance benchmarking
- [ ] Custom model support
- [ ] Advanced prompt engineering patterns

---

*Built for efficient CPU-only inference within Streamlit Cloud's 1GB RAM constraints.*
