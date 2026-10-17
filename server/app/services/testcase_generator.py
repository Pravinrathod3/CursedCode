"""
AI-Powered Test Case & Edge Case Generator.
Uses OpenRouter to generate comprehensive visible tests and hidden edge cases
for algorithm problems, validating syntax and format before database insertion.
"""
import ast
import json
import re
from app.integrations.llm_client import chat_completion
from app.core.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a Principal Test Engineer and Competitive Programming Judge Architect.
Your job is to generate rigorous, exhaustive, zero-flaw Python test cases for algorithm challenges.

For every problem, you MUST produce:
1. Exactly 3 `visible_tests` (canonical standard examples to help the learner understand).
2. Exactly 5 to 7 `hidden_tests` specifically targeting CRITICAL EDGE CASES:
   - Empty input (e.g. empty array `[]`, empty string `""`, `0`) if valid by problem contract.
   - Minimal boundary size (e.g. single element array `[5]`, single character `"a"`, `k=0`).
   - Extreme values / signs (negative numbers, zeroes, large integers within limits).
   - Duplicates and uniform collections (e.g. `[7, 7, 7, 7]`, all identical characters).
   - Order variations (strictly increasing, strictly decreasing, unordered, alternating).
   - No-solution or failure scenarios (target not present -> returns -1 or False or empty).
   - Stress / parity boundaries (odd vs even lengths, boundary divisors).
3. Exactly 4 progressive `hints`:
   - Hint 1: Conceptual nudge.
   - Hint 2: Logical inspection direction.
   - Hint 3: Specific guidance.
   - Hint 4: Surgical fix direction.

Return strictly raw JSON with NO markdown formatting, NO backticks, and NO conversational text.
Format:
{
  "function_name": "<exact_python_function_name>",
  "visible_tests": [
    {"call": "<valid_python_call_string>", "expected": "<stringified_return_value>", "description": "<short_purpose>"}
  ],
  "hidden_tests": [
    {"call": "<valid_python_call_string>", "expected": "<stringified_return_value>", "description": "<edge_case_type_and_purpose>"}
  ],
  "hints": [
    "<hint 1>", "<hint 2>", "<hint 3>", "<hint 4>"
  ]
}
"""


def _sanitize_json_response(raw_text: str) -> str:
    """Extract valid JSON from LLM output, stripping markdown fences if present."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    
    # Locate first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return text


def _validate_call_syntax(call_expr: str) -> bool:
    """Validate that the call expression parses as a valid Python call."""
    try:
        tree = ast.parse(call_expr.strip(), mode="eval")
        return isinstance(tree.body, ast.Call)
    except Exception:
        return False


def _format_expected_value(val: any) -> str:
    """Normalize expected value to string representation matching judge engine."""
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        # If it's already a stringified boolean or int
        if val.strip() in ("True", "False"):
            return val.strip()
        return val
    try:
        return json.dumps(val)
    except Exception:
        return str(val)


async def generate_testcases_for_problem(
    title: str,
    statement: str,
    function_signature: str = "",
    starter_code: str = "",
    difficulty: str = "Medium",
    tags: list[str] | None = None,
) -> dict:
    """
    Call OpenRouter to generate comprehensive visible tests, hidden edge cases, and progressive hints.
    """
    tags_str = ", ".join(tags or [])
    user_prompt = f"""Generate exhaustive test cases and edge cases for this challenge:

TITLE: {title}
DIFFICULTY: {difficulty}
TAGS: {tags_str}
STATEMENT:
{statement}

FUNCTION SIGNATURE: {function_signature}
STARTER CODE:
{starter_code}

Ensure all `call` fields are valid Python function invocations that can be parsed by `ast.parse`.
Make sure `expected` represents the exact output of a correct algorithm.
Include edge cases for empty collections, single elements, negative numbers, duplicates, and boundary limits.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    try:
        raw_output = await chat_completion(messages, max_tokens=1500)
        clean_json_str = _sanitize_json_response(raw_output)
        data = json.loads(clean_json_str)

        visible_tests = []
        for i, tc in enumerate(data.get("visible_tests", []), start=1):
            call_expr = tc.get("call", "").strip()
            if _validate_call_syntax(call_expr):
                visible_tests.append({
                    "test": i,
                    "call": call_expr,
                    "expected": _format_expected_value(tc.get("expected", "")),
                    "description": tc.get("description", f"Visible Test {i}"),
                    "visibility": "visible"
                })

        hidden_tests = []
        for i, tc in enumerate(data.get("hidden_tests", []), start=len(visible_tests) + 1):
            call_expr = tc.get("call", "").strip()
            if _validate_call_syntax(call_expr):
                hidden_tests.append({
                    "test": i,
                    "call": call_expr,
                    "expected": _format_expected_value(tc.get("expected", "")),
                    "description": tc.get("description", f"Edge Case {i}"),
                    "visibility": "hidden"
                })

        # Ensure we have at least 2 visible and 3 hidden tests
        if len(visible_tests) < 2 or len(hidden_tests) < 3:
            raise ValueError("LLM generated insufficient valid test cases.")

        return {
            "function_name": data.get("function_name", ""),
            "visible_tests": visible_tests,
            "hidden_tests": hidden_tests,
            "hints": data.get("hints", [
                "Carefully consider input constraints and boundary cases.",
                "Inspect variables before and after loop iterations.",
                "Review edge case handling for short or empty inputs.",
                "Verify return values match expected types."
            ])
        }

    except Exception as exc:
        logger.warning("Dynamic test generation fallback triggered: %s", exc)
        return _generate_fallback_testcases(title, statement, function_signature)


def _generate_fallback_testcases(title: str, statement: str, function_signature: str) -> dict:
    """Deterministic fallback test generator when LLM is unavailable."""
    fn_name = "solution"
    if function_signature and "(" in function_signature:
        fn_name = function_signature.split("(")[0].replace("def ", "").strip()
    elif "named `" in statement:
        match = re.search(r"named `([a-zA-Z0-9_]+)\(", statement)
        if match:
            fn_name = match.group(1)

    return {
        "function_name": fn_name,
        "visible_tests": [
            {"test": 1, "call": f"{fn_name}([1, 2, 3])", "expected": "3", "description": "Standard positive sequence", "visibility": "visible"},
            {"test": 2, "call": f"{fn_name}([10, 20, 30])", "expected": "30", "description": "Multiples of 10", "visibility": "visible"},
            {"test": 3, "call": f"{fn_name}([0])", "expected": "0", "description": "Single element zero", "visibility": "visible"}
        ],
        "hidden_tests": [
            {"test": 4, "call": f"{fn_name}([])", "expected": "0", "description": "Edge case: empty list", "visibility": "hidden"},
            {"test": 5, "call": f"{fn_name}([-5, -10])", "expected": "-5", "description": "Edge case: negative values", "visibility": "hidden"},
            {"test": 6, "call": f"{fn_name}([100, 100, 100])", "expected": "100", "description": "Edge case: duplicate elements", "visibility": "hidden"},
            {"test": 7, "call": f"{fn_name}([999999])", "expected": "999999", "description": "Edge case: boundary large value", "visibility": "hidden"},
            {"test": 8, "call": f"{fn_name}([5, 4, 3, 2, 1])", "expected": "5", "description": "Edge case: reverse sorted order", "visibility": "hidden"}
        ],
        "hints": [
            "Consider the basic properties of the input collection and its elements.",
            "Verify how the boundary indices and edge elements are processed.",
            "Inspect edge cases such as empty lists, negative inputs, and single elements.",
            "Ensure the function returns the value rather than printing it."
        ]
    }
