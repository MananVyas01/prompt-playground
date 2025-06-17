"""
Fake LLM simulator for safe and fast testing
"""


def fake_llm(prompt: str) -> str:
    """
    Simulate LLM responses based on prompt content.
    
    Args:
        prompt (str): Input prompt text
        
    Returns:
        str: Simulated response
    """
    prompt_lower = prompt.lower()

    if "hello" in prompt_lower:
        return "Hi there! How can I assist you today?"

    if "summarize" in prompt_lower:
        return "Here's a quick summary: [Insert concise version of your input]"

    if "def " in prompt_lower or "python" in prompt_lower:
        return "Sure! Here's a basic Python function:\n\ndef example_function():\n    pass"

    if "explain" in prompt_lower:
        return "Let me explain it in simple terms: [Explanation goes here]"

    return "This is a simulated response from FakeGPT based on your input!"
