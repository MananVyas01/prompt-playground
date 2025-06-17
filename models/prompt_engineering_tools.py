"""
Prompt Engineering Tools for professional prompt optimization
"""

def prompt_refiner(prompt: str) -> str:
    """
    AI-powered prompt optimization and refinement
    """
    prompt_stripped = prompt.strip()
    prompt_lower = prompt_stripped.lower()
    
    if len(prompt_stripped) < 10:
        return f"**OPTIMIZED PROMPT:**\n\nPlease provide a detailed and comprehensive response to: '{prompt_stripped}'\n\nEnsure your response includes:\n• Relevant context and background\n• Specific examples and use cases\n• Clear, actionable information\n• Well-structured presentation"
    
    # Advanced prompt optimization based on type
    if any(word in prompt_lower for word in ["code", "function", "programming", "development"]):
        return f"**OPTIMIZED PROMPT:**\n\n{prompt_stripped}\n\n**Requirements:**\n1. Provide working, commented code examples\n2. Explain the logic and methodology\n3. Include error handling and edge cases\n4. Suggest optimizations and alternatives\n5. Add relevant documentation and best practices"
    
    if any(word in prompt_lower for word in ["explain", "describe", "what is", "how does"]):
        return f"**OPTIMIZED PROMPT:**\n\n{prompt_stripped}\n\n**Structure your response with:**\n• **Definition**: Clear, concise explanation\n• **Context**: Why this matters and when to use it\n• **Examples**: Real-world applications and scenarios\n• **Key Points**: Most important takeaways\n• **Further Reading**: Related concepts or resources"
    
    if any(word in prompt_lower for word in ["compare", "versus", "difference", "pros and cons"]):
        return f"**OPTIMIZED PROMPT:**\n\n{prompt_stripped}\n\n**Provide comprehensive comparison:**\n• **Overview**: Brief introduction to items being compared\n• **Similarities**: What they have in common\n• **Key Differences**: Major distinguishing factors\n• **Pros & Cons**: Advantages and disadvantages of each\n• **Use Cases**: When to choose one over the other\n• **Recommendation**: Best choice for specific scenarios"
    
    if any(word in prompt_lower for word in ["analyze", "review", "evaluate", "assessment"]):
        return f"**OPTIMIZED PROMPT:**\n\n{prompt_stripped}\n\n**Framework for analysis:**\n• **Executive Summary**: Key findings upfront\n• **Methodology**: How the analysis was conducted\n• **Key Findings**: Major discoveries and insights\n• **Evidence**: Supporting data and examples\n• **Implications**: What this means and why it matters\n• **Recommendations**: Actionable next steps"
    
    # Default optimization
    return f"**OPTIMIZED PROMPT:**\n\n{prompt_stripped}\n\n**Enhancement Guidelines:**\n• Provide comprehensive, well-researched information\n• Use clear structure with headers and bullet points\n• Include relevant examples and practical applications\n• Ensure accuracy and cite sources where appropriate\n• Make the response actionable and valuable to the reader"


def prompt_analyzer(prompt: str) -> str:
    """
    Analyze prompt structure and provide optimization suggestions
    """
    prompt_stripped = prompt.strip()
    analysis = []
    
    # Length analysis
    word_count = len(prompt_stripped.split())
    if word_count < 5:
        analysis.append("❌ **Length**: Too short - consider adding more context")
    elif word_count < 15:
        analysis.append("⚠️ **Length**: Could be more detailed for better results")
    else:
        analysis.append("✅ **Length**: Good detail level")
    
    # Clarity analysis
    if any(word in prompt_stripped.lower() for word in ["please", "could you", "would you"]):
        analysis.append("✅ **Tone**: Polite and professional")
    else:
        analysis.append("⚠️ **Tone**: Consider adding polite language")
    
    # Specificity analysis
    if any(word in prompt_stripped.lower() for word in ["specific", "detailed", "example", "step"]):
        analysis.append("✅ **Specificity**: Requests specific information")
    else:
        analysis.append("❌ **Specificity**: Too vague - add specific requirements")
    
    # Structure analysis
    if "?" in prompt_stripped:
        analysis.append("✅ **Structure**: Clear question format")
    else:
        analysis.append("⚠️ **Structure**: Consider framing as a clear question")
    
    # Context analysis
    if any(word in prompt_stripped.lower() for word in ["context", "background", "situation", "scenario"]):
        analysis.append("✅ **Context**: Provides situational context")
    else:
        analysis.append("❌ **Context**: Missing background information")
    
    return f"**PROMPT ANALYSIS:**\n\n**Original Prompt:** {prompt_stripped}\n\n**Analysis Results:**\n" + "\n".join(analysis) + f"\n\n**Overall Score:** {len([a for a in analysis if '✅' in a])}/5\n\n**Recommendations:**\n• Add more specific requirements\n• Include relevant context and background\n• Use professional, polite language\n• Request structured responses"


def few_shot_generator(prompt: str) -> str:
    """
    Generate few-shot examples for better prompt engineering
    """
    prompt_stripped = prompt.strip()
    
    return f"""**FEW-SHOT PROMPT TEMPLATE:**

**Instruction:** {prompt_stripped}

**Example 1:**
Input: [Sample input similar to your use case]
Expected Output: [High-quality example response]

**Example 2:**
Input: [Another relevant sample input]
Expected Output: [Another high-quality example response]

**Example 3:**
Input: [Third sample input with slight variation]
Expected Output: [Third example showing consistency]

**Your Task:**
Input: [Your actual input here]
Expected Output: [Follow the pattern and quality shown above]

**Guidelines:**
- Maintain consistency with the examples
- Follow the same format and structure
- Ensure high quality and accuracy
- Include relevant details as shown"""


def cot_builder(prompt: str) -> str:
    """
    Build Chain-of-Thought prompts for better reasoning
    """
    prompt_stripped = prompt.strip()
    
    return f"""**CHAIN-OF-THOUGHT PROMPT:**

{prompt_stripped}

**Reasoning Process:**
Let's work through this step by step:

**Step 1: Understanding**
- First, let me understand what is being asked
- Identify the key components and requirements
- Consider any constraints or limitations

**Step 2: Analysis**
- Break down the problem into smaller parts
- Consider different approaches or perspectives
- Evaluate potential solutions or responses

**Step 3: Synthesis**
- Combine insights from the analysis
- Develop a comprehensive response
- Ensure logical flow and consistency

**Step 4: Validation**
- Check the response for accuracy and completeness
- Verify it addresses all aspects of the question
- Consider potential follow-up questions

**Final Response:**
[Provide your well-reasoned, step-by-step answer here]

**Note:** This chain-of-thought approach ensures thorough analysis and high-quality responses."""
