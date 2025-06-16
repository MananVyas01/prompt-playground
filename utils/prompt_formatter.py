"""
Prompt formatting utilities for the Prompt Playground app.
Handles template processing, placeholder replacement, and prompt formatting.
"""

import re
from typing import Dict, List, Tuple


def format_prompt(template: str, input_text: str) -> str:
    """
    Format a prompt template by replacing placeholders with actual input text.

    Args:
        template (str): The prompt template with placeholders
        input_text (str): The user input text to replace placeholders

    Returns:
        str: The formatted prompt with placeholders replaced
    """
    if not template or not input_text:
        return template

    # Replace common placeholder patterns
    formatted = template.replace("{input}", input_text)
    formatted = formatted.replace("{INPUT}", input_text)
    formatted = formatted.replace("[INPUT]", input_text)
    formatted = formatted.replace("<input>", input_text)

    return formatted.strip()


def extract_placeholders(template: str) -> List[str]:
    """
    Extract all placeholders from a template.

    Args:
        template (str): The template string

    Returns:
        List[str]: List of placeholder names found in the template
    """
    placeholders = []

    # Find {placeholder} patterns
    curly_matches = re.findall(r"\{([^}]+)\}", template)
    placeholders.extend(curly_matches)

    # Find [placeholder] patterns
    square_matches = re.findall(r"\[([^\]]+)\]", template)
    placeholders.extend(square_matches)

    # Find <placeholder> patterns
    angle_matches = re.findall(r"<([^>]+)>", template)
    placeholders.extend(angle_matches)

    return list(set(placeholders))  # Remove duplicates


def validate_template(template: str) -> Tuple[bool, str]:
    """
    Validate a prompt template for common issues.

    Args:
        template (str): The template to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not template.strip():
        return False, "Template cannot be empty"

    placeholders = extract_placeholders(template)

    if not placeholders:
        return False, "Template should contain at least one placeholder (e.g., {input})"

    # Check for unmatched brackets
    open_curly = template.count("{")
    close_curly = template.count("}")
    if open_curly != close_curly:
        return False, "Unmatched curly brackets in template"

    open_square = template.count("[")
    close_square = template.count("]")
    if open_square != close_square:
        return False, "Unmatched square brackets in template"

    open_angle = template.count("<")
    close_angle = template.count(">")
    if open_angle != close_angle:
        return False, "Unmatched angle brackets in template"

    return True, ""


def get_template_preview(template: str, sample_input: str = "your input here") -> str:
    """
    Generate a preview of how the template will look with sample input.

    Args:
        template (str): The template string
        sample_input (str): Sample input to use for preview

    Returns:
        str: Preview of the formatted template
    """
    return format_prompt(template, sample_input)


def suggest_input_placeholder(prompt_type: str) -> str:
    """
    Suggest an appropriate input placeholder based on prompt type.

    Args:
        prompt_type (str): The type of prompt

    Returns:
        str: Suggested placeholder text
    """
    suggestions = {
        "instruction": "Write a specific instruction or task",
        "zero-shot": "Ask a question or describe a problem",
        "few-shot": "Ask a question similar to the examples",
        "chain-of-thought": "Describe a complex problem to solve step-by-step",
        "role-playing": "Describe what you want the assistant to help with",
        "creative": "Describe what you want to create or write",
        "analysis": "Provide text or data to analyze",
        "translation": "Enter text to translate",
        "summarization": "Provide text to summarize",
    }

    prompt_type_lower = prompt_type.lower()

    # Try exact match first
    if prompt_type_lower in suggestions:
        return suggestions[prompt_type_lower]

    # Try partial matches
    for key, value in suggestions.items():
        if key in prompt_type_lower or prompt_type_lower in key:
            return value

    # Default fallback
    return "Enter your input here"


def count_tokens_estimate(text: str) -> int:
    """
    Rough estimation of token count for a given text.

    Args:
        text (str): Input text

    Returns:
        int: Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters for English text
    return len(text) // 4 + text.count(" ") + 1


def truncate_for_model(text: str, max_tokens: int = 512) -> str:
    """
    Truncate text to fit within token limits.

    Args:
        text (str): Input text
        max_tokens (int): Maximum allowed tokens

    Returns:
        str: Truncated text if necessary
    """
    estimated_tokens = count_tokens_estimate(text)

    if estimated_tokens <= max_tokens:
        return text

    # Rough truncation based on character count
    target_chars = max_tokens * 4
    if len(text) > target_chars:
        return text[:target_chars] + "..."

    return text
