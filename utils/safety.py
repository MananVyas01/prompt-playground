"""
Safety utilities for the Prompt Playground
"""

try:
    from better_profanity import profanity
    PROFANITY_AVAILABLE = True
except ImportError:
    PROFANITY_AVAILABLE = False
    profanity = None


def safe_format_prompt(user_input: str) -> str:
    """
    Wrap user input in a safe, instruction-style template to encourage
    helpful and appropriate responses.
    
    Args:
        user_input: The raw user input
        
    Returns:
        Formatted prompt with safety guidelines
    """
    return f"""You are a helpful assistant. Respond clearly and politely.

User: {user_input}
Assistant:"""


def filter_output(text: str):
    """
    Filter potentially inappropriate content from model output.
    
    Args:
        text: Raw model output
        
    Returns:
        Tuple of (filtered_text, was_filtered)
    """
    if not PROFANITY_AVAILABLE:
        return text, False
        
    # Load profanity filter if not already loaded
    if not hasattr(profanity, '_words'):
        profanity.load_censor_words()
    
    if profanity.contains_profanity(text):
        return "[⚠️ Filtered: Output contained inappropriate content]", True
    
    return text, False


def validate_input(user_input: str):
    """
    Validate user input for safety concerns.
    
    Args:
        user_input: User's input text
        
    Returns:
        Tuple of (message, is_valid)
    """
    if not user_input.strip():
        return "Please enter some text", False
    
    if len(user_input) > 1000:
        return "Input too long (max 1000 characters)", False
    
    # Check for potential prompt injection attempts
    injection_patterns = [
        "ignore previous instructions",
        "forget your instructions", 
        "act as if you are",
        "pretend to be",
    ]
    
    user_lower = user_input.lower()
    for pattern in injection_patterns:
        if pattern in user_lower:
            return f"⚠️ Input may contain prompt injection attempt: '{pattern}'", False
    
    return "", True
