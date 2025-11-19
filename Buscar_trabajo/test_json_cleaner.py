import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import clean_json_response

def test_cleaner():
    print("🧪 Testing clean_json_response...")
    
    # Case 1: Pure JSON
    case1 = '{"key": "value"}'
    assert clean_json_response(case1) == '{"key": "value"}', "Failed Case 1"
    print("✅ Case 1 Passed: Pure JSON")

    # Case 2: Markdown block
    case2 = '```json\n{"key": "value"}\n```'
    assert clean_json_response(case2) == '{"key": "value"}', "Failed Case 2"
    print("✅ Case 2 Passed: Markdown block")

    # Case 3: Markdown block with text around (simple strip check)
    # Note: The current implementation only strips the wrapper, not text *outside* the wrapper if it's not whitespace.
    # But usually Gemini returns just the block or the block with whitespace.
    case3 = '   ```json\n{"key": "value"}\n```   '
    assert clean_json_response(case3) == '{"key": "value"}', "Failed Case 3"
    print("✅ Case 3 Passed: Whitespace around block")

    # Case 4: Generic code block
    case4 = '```\n{"key": "value"}\n```'
    assert clean_json_response(case4) == '{"key": "value"}', "Failed Case 4"
    print("✅ Case 4 Passed: Generic code block")

    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_cleaner()
