# 🧠 Prompt Playground Lite

**Prompt Playground Lite** is an interactive Streamlit app built for prompt engineers, LLM researchers, and curious developers to test different types of prompts on small, CPU-friendly language models — all within the constraints of free-tier Streamlit Cloud (1GB RAM, no GPU).

🔗 **Live Demo:** [👉 Try the App](https://prompt-playground-lite.streamlit.app/)

---

## 🚀 Features

- 🧠 **Prompt Type Selector**: Choose from Instruction, Zero-shot, Few-shot, Chain-of-Thought, and Role-Playing prompts
- 🛠️ **Smart Prompt Templates**: Auto-fill templates with validation and real-time input injection
- 🤖 **Multi-Model Comparison**: Test up to 3 lightweight models side-by-side
- 📊 **Performance Analysis**: Generation timing and response difference highlighting
- 🔁 **Interactive Controls**: Regenerate responses and copy individual outputs
- 💾 **Export Functionality**: Download prompts and responses as `.txt` or `.md` files
- 🎨 **Theme Customization**: Dark/Light mode toggle with custom branding
- 💭 **Session Memory**: Remember previous prompts and responses (up to 10 sessions)
- 📱 **Responsive UI**: Clean, intuitive interface with progress indicators
- ⚡ **CPU-Optimized**: Runs efficiently on free-tier cloud hosting

---

## 📂 Project Structure

```bash
prompt-playground/
├── app.py                     # Main Streamlit application
├── prompt_types.json          # Prompt templates and descriptions
├── models/
│   ├── __init__.py           # Models package initialization
│   └── load_model.py         # Model loading and inference utilities
├── utils/
│   ├── __init__.py           # Utils package initialization
│   └── prompt_formatter.py  # Prompt formatting and validation
├── assets/
│   ├── logo.svg              # App logo (SVG format)
│   └── logo.png              # Logo fallback (PNG)
├── .streamlit/
│   └── config.toml           # Streamlit theme and server configuration
├── requirements.txt          # Python dependencies
├── .gitignore               # Git exclusions
└── README.md                # This documentation
```

---

## ⚙️ Tech Stack

- **Frontend**: Streamlit 1.28+
- **ML Framework**: Transformers (Hugging Face) + PyTorch
- **Language**: Python 3.8+
- **Deployment**: Streamlit Cloud (CPU-only)

### 🤖 Supported Models

Small, CPU-friendly language models optimized for 1GB RAM environments:

- `sshleifer/tiny-gpt2` - Ultra-lightweight GPT-2 variant (42MB)
- `distilgpt2` - Distilled version of GPT-2 (353MB)
- `microsoft/DialoGPT-small` - Conversational AI model (117MB)
- `gpt2` - Standard GPT-2 for comparison (548MB)

---

## � Setup Instructions

### Local Development

```bash
# Clone the repository
git clone https://github.com/MananVyas01/prompt-playground.git
cd prompt-playground

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Environment Requirements

```bash
# Minimum requirements
Python >= 3.8
RAM >= 2GB (for local development)
CPU-only (no GPU required)
```

---

## ☁️ Deployment on Streamlit Cloud

1. **Push to GitHub**: Commit your code to a GitHub repository
2. **Connect to Streamlit Cloud**: 
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch and `app.py`
3. **Deploy**: Streamlit will automatically install dependencies and deploy
4. **Optional**: Add Hugging Face token in Streamlit Secrets for private models

### Deployment Configuration

The app is pre-configured for Streamlit Cloud with:
- CPU-only model inference
- Memory-efficient caching
- Optimized for 1GB RAM limit
- Automatic dependency management

---

## 🎯 Usage Guide

### Getting Started

1. **Select Prompt Type**: Choose from pre-configured templates (Instruction, Few-shot, etc.)
2. **Enter Your Input**: Fill in the text area with your specific query or content
3. **Choose Models**: Select 1-3 lightweight models for comparison
4. **Generate**: Click the generate button to see model responses
5. **Compare & Export**: Analyze differences and download results

### Advanced Features

- **Session Memory**: Enable "Remember my session" to store previous interactions
- **Theme Toggle**: Switch between light and dark modes
- **Export Options**: Download formatted results as TXT or Markdown
- **Response Analysis**: View generation times and textual differences
- **Template Editing**: Modify prompt templates for custom use cases

---

## 📋 Available Prompt Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Instruction** | Direct instruction-following format | Clear, specific tasks |
| **Zero-shot** | No examples, relies on training knowledge | General queries |
| **Few-shot** | Includes examples to guide responses | Pattern recognition |
| **Chain-of-Thought** | Encourages step-by-step reasoning | Complex problem solving |
| **Role-Playing** | Assigns specific personas to the model | Creative/contextual responses |

---

## 🛠️ Customization

### Adding New Prompt Types

Edit `prompt_types.json` to add custom templates:

```json
{
  "your_prompt_type": {
    "template": "Your template with {USER_INPUT} placeholder",
    "description": "Description of your prompt type",
    "input_placeholder": "Guidance for users"
  }
}
```

### Adding New Models

Modify `models/load_model.py` to include additional lightweight models:

```python
def load_models() -> List[str]:
    return [
        "your/custom-model",
        # ... existing models
    ]
```

### Theme Customization

Edit `.streamlit/config.toml` to customize colors and appearance:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

---

## 📊 Performance Metrics

- **Model Loading**: ~2-5 seconds for lightweight models
- **Inference Speed**: 1-3 seconds per response (CPU-only)
- **Memory Usage**: <1GB total (including Streamlit overhead)
- **Concurrent Users**: Supports multiple users on Streamlit Cloud

---

## 🤝 Contributing

Pull requests are welcome! Areas for contribution:

- 🆕 **New Prompt Types**: Add innovative prompting strategies
- 🤖 **Model Integration**: Support for additional lightweight models
- 🎨 **UI Improvements**: Enhanced user experience and accessibility
- 📊 **Analytics**: Better response analysis and metrics
- 🔧 **Performance**: Optimization for faster inference

### Development Setup

```bash
# Fork the repository
git clone https://github.com/your-username/prompt-playground-lite.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
streamlit run app.py

# Submit pull request
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## � Credits & Acknowledgements

- **Built by**: [Manan Vyas](https://github.com/MananVyas01) 
- **Powered by**: Open-source LLMs via [Hugging Face](https://huggingface.co)
- **Framework**: [Streamlit](https://streamlit.io) for the amazing web app framework
- **Inspiration**: The growing need for accessible prompt engineering tools
- **Community**: Thanks to all contributors and users providing feedback

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/prompt-playground-lite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/prompt-playground-lite/discussions)
- **Documentation**: This README and inline code comments

---

## 🚀 Roadmap

- [ ] **Prompt Optimization**: AI-powered prompt improvement suggestions
- [ ] **Model Benchmarking**: Automated performance comparison across models
- [ ] **Custom Model Upload**: Support for user-provided lightweight models
- [ ] **Advanced Analytics**: Response quality metrics and visualization
- [ ] **API Integration**: REST API for programmatic access
- [ ] **Collaborative Features**: Share and discover community prompts

---

*Built with ❤️ for the AI community. Happy prompting! By MananVyas01 🧠✨*
