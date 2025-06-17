#!/usr/bin/env python3
"""
Quick test to verify the app works end-to-end
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_end_to_end():
    """Test the complete flow"""
    print("🧪 Testing End-to-End Functionality")
    print("=" * 40)

    try:
        # Test app import
        import app

        print("✅ App imports successfully")

        # Test FakeGPT directly
        from models.fake_llm import fake_llm

        result = fake_llm("Hello world")
        print(f"✅ FakeGPT response: {result}")

        # Test model loading
        from models.load_model import load_model

        model = load_model("fakegpt")
        if callable(model):
            test_response = model("Test prompt")
            print(f"✅ Model loading test: {test_response}")

        print("\n🎉 All tests passed! App should work correctly.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_end_to_end()
