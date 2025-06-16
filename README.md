# 🧠 Prompt Playground

A lightweight, Streamlit-based prompt engineering playground using Hugging Face models. Explore, test, and compare different prompt types like zero-shot, few-shot, and instruction prompts with small CPU-optimized language models.

## ✨ Features

- **Interactive UI**: Clean Streamlit interface for prompt experimentation
- **Multiple Prompt Types**: Pre-configured templates for different prompting strategies
- **Live Model Inference**: Real-time text generation with Hugging Face models
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

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── models/               
│   ├── __init__.py       # Models package initialization
│   └── load_model.py     # Model loading and inference utilities
├── prompt_types.json      # Prompt templates and descriptions
├── requirements.txt       # Python dependencies
├── .streamlit/           
│   └── config.toml       # Streamlit configuration
└── README.md            # This file
```

## 🎯 Roadmap

- [x] Stage 1: ✅ Initialize Project & UI Skeleton 
- [x] Stage 2: ✅ Add model inference capabilities
- [x] Stage 3: ✅ Prompt Template Autofill Engine + Smart UI
- [ ] Stage 4: Add prompt optimization suggestions

---

*Built for efficient CPU-only inference within Streamlit Cloud's 1GB RAM constraints.*
