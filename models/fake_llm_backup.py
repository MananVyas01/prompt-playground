def fake_llm(prompt: str) -> str:
    """
    Refine and improve the user's input prompt to make it more effective for LLMs.

    Args:
        prompt (str): User's original prompt

    Returns:
        str: Refined and improved version of the prompt
    """
    prompt_stripped = prompt.strip()
    prompt_lower = prompt_stripped.lower()

    # If prompt is too short or vague, add structure and context
    if len(prompt_stripped) < 10:
        return f"**REFINED PROMPT:**\n\nPlease provide a detailed and helpful response to: '{prompt_stripped}'\n\nInclude relevant context, examples, and clear explanations in your answer."

    # Detect and improve code-related prompts
    if any(
        word in prompt_lower
        for word in [
            "code",
            "function",
            "programming",
            "python",
            "javascript",
            "html",
            "css",
        ]
    ):
        if "example" not in prompt_lower and "how to" not in prompt_lower:
            return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nPlease provide:\n1. A working code example\n2. Step-by-step explanation\n3. Best practices or common pitfalls\n4. Alternative approaches if applicable"
        else:
            return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nEnsure your response includes commented code and practical examples."

    # Improve explanation requests
    if any(
        word in prompt_lower
        for word in ["explain", "what is", "how does", "why", "definition"]
    ):
        if "simple" not in prompt_lower and "example" not in prompt_lower:
            return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nPlease explain this in simple terms with:\n- Clear definitions\n- Real-world examples\n- Step-by-step breakdown if applicable\n- Key takeaways"
        else:
            return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nProvide a comprehensive explanation with examples and practical applications."

    # Enhance comparison requests
    if any(
        word in prompt_lower
        for word in ["compare", "difference", "vs", "versus", "better"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nProvide a detailed comparison including:\n- Key similarities and differences\n- Pros and cons of each option\n- Use cases for each\n- Recommendation based on specific scenarios"

    # Improve creative writing prompts
    if any(
        word in prompt_lower
        for word in ["write", "story", "poem", "creative", "imagine"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nPlease create this with:\n- Vivid descriptions and engaging language\n- Clear structure and flow\n- Appropriate tone and style\n- Attention to detail and creativity"

    # Enhance problem-solving prompts
    if any(
        word in prompt_lower
        for word in ["solve", "problem", "issue", "fix", "debug", "error"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nPlease provide:\n1. Problem analysis and root cause\n2. Step-by-step solution\n3. Prevention strategies\n4. Alternative solutions if available"

    # Improve summarization requests
    if any(
        word in prompt_lower for word in ["summarize", "summarise", "summary", "tldr"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nProvide a structured summary with:\n- Key points and main ideas\n- Important details and context\n- Clear, concise language\n- Actionable insights if applicable"

    # Enhance how-to requests
    if any(
        word in prompt_lower
        for word in ["how to", "guide", "tutorial", "step", "process"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nProvide a comprehensive guide with:\n1. Prerequisites and requirements\n2. Detailed step-by-step instructions\n3. Tips and best practices\n4. Common mistakes to avoid\n5. Additional resources"

    # Improve list/recommendation requests
    if any(
        word in prompt_lower
        for word in ["list", "recommend", "suggest", "ideas", "options"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nProvide organized recommendations with:\n- Categorized or prioritized list\n- Brief explanation for each item\n- Criteria used for selection\n- Additional context or alternatives"

    # Enhance analysis requests
    if any(
        word in prompt_lower
        for word in ["analyze", "analysis", "review", "evaluate", "assess"]
    ):
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nProvide a thorough analysis including:\n- Structured evaluation framework\n- Key findings and insights\n- Supporting evidence or reasoning\n- Conclusions and implications"

    # Default refinement for general prompts
    if prompt_stripped.endswith("?"):
        # Question format - add context request
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nPlease provide a comprehensive answer with relevant context, examples, and clear explanations."
    else:
        # Statement format - add structure and detail request
        return f"**REFINED PROMPT:**\n\n{prompt_stripped}\n\nPlease elaborate on this topic with:\n- Detailed information and context\n- Relevant examples or case studies\n- Practical applications or implications\n- Clear and organized presentation"
