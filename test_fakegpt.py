#!/usr/bin/env python3
"""
Test script to verify FakeGPT integration works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fakegpt_integration():
    """Test FakeGPT integration"""
    print("🧪 Testing FakeGPT Integration")
    print("=" * 40)
    
    # Test 1: Import fake_llm
    try:
        from models.fake_llm import fake_llm
        print("✅ Successfully imported fake_llm")
    except ImportError as e:
        print(f"❌ Failed to import fake_llm: {e}")
        return False
    
    # Test 2: Test direct function calls
    test_cases = [
        ("hello world", "Hi there! How can I assist you today?"),
        ("explain this", "Let me explain it in simple terms: [Explanation goes here]"),
        ("summarize text", "Here's a quick summary: [Insert concise version of your input]"),
        ("def function():", "Sure! Here's a basic Python function:"),
        ("random input", "This is a simulated response from FakeGPT based on your input!")
    ]
    
    for prompt, expected_start in test_cases:
        result = fake_llm(prompt)
        if result.startswith(expected_start.split(":")[0]):
            print(f"✅ '{prompt}' -> correct response pattern")
        else:
            print(f"❌ '{prompt}' -> unexpected response: {result[:50]}...")
    
    # Test 3: Test model loading
    try:
        from models.load_model import load_model
        model = load_model("fakegpt")
        if model == fake_llm:
            print("✅ FakeGPT loads correctly through load_model")
        else:
            print("❌ FakeGPT not loading correctly")
    except Exception as e:
        print(f"❌ Error loading FakeGPT: {e}")
    
    # Test 4: Test model info
    try:
        from models.load_model import get_model_info
        info = get_model_info("fakegpt")
        if info["type"] == "FakeGPT Simulator":
            print("✅ FakeGPT model info correct")
        else:
            print(f"❌ Wrong model info: {info}")
    except Exception as e:
        print(f"❌ Error getting model info: {e}")
    
    print("\n🎉 FakeGPT integration test complete!")
    return True

if __name__ == "__main__":
    test_fakegpt_integration()
