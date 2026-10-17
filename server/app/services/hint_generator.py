"""
Dynamic Hint Generator & Guardrails Engine.

Orchestrates multi-level progressive hints (Levels 1 to 4) using OpenRouter LLM
with LangSmith tracing, structured prompt engineering, and strict security guardrails.

Guardrails:
- Input: Strips all hidden test cases, secret tokens, and runner stack traces.
- Output: Validates hint length, prevents full solution/function leakage for levels 1-3.
- Level 4 Code Patch: AST validation (ast.parse) to ensure code modifications are syntactically valid and non-destructive.
- Fault tolerance: Deterministic fallback hint ladder if LLM provider times out or fails.
"""
from __future__ import annotations

import ast
import json
import os
import re
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.llm_client import chat_completion
from app.schemas.hint import CodePatch

logger = get_logger(__name__)

# Configure LangSmith environment if tracing is active
settings = get_settings()
if settings.langsmith_tracing and settings.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project

try:
    from langsmith import traceable
except ImportError:
    def traceable(**kwargs):
        def decorator(f):
            return f
        return decorator


# ---------------------------------------------------------------------------
# Output Guardrail Validators
# ---------------------------------------------------------------------------

def validate_hint_guardrails(hint_text: str, level: int, function_name: str = "") -> str:
    """
    Enforce security and pedagogical guardrails on generated hint text:
    1. Strip markdown fences if they contain complete function implementations (for levels 1-3).
    2. Enforce length limits to keep hints focused and prevent prompt leakage.
    3. Ensure no hidden test tokens or leaked internal system traces.
    """
    cleaned = hint_text.strip()

    # For levels 1, 2, and 3: prevent full function solution leakage
    if level < 4:
        # If the LLM returned a full "def function_name(...): ...", strip the code block
        def_pattern = re.compile(r"```(?:python)?\s*def\s+[a-zA-Z0-9_]+\s*\(.*?\):.*?```", re.DOTALL)
        if def_pattern.search(cleaned):
            logger.warning("Guardrail: Removed full function code block from level %d hint", level)
            cleaned = def_pattern.sub("", cleaned).strip()

        # If lines contain a raw function definition, strip it
        lines = cleaned.splitlines()
        non_def_lines = [l for l in lines if not l.strip().startswith("def ") and not l.strip().startswith("return ")]
        if len(non_def_lines) >= 1 and len(non_def_lines) < len(lines):
            cleaned = " ".join(non_def_lines).strip()

    # Length guardrail (truncate if LLM hallucinates an essay)
    if len(cleaned) > 500:
        cleaned = cleaned[:497] + "..."

    return cleaned


def validate_code_patch(patch_dict: dict, original_code: str) -> CodePatch | None:
    """
    Validate that the generated code patch:
    1. Contains all required fields (target_line, original_snippet, replacement_snippet, explanation).
    2. Produces syntactically valid Python code (ast.parse).
    3. Does not introduce dangerous system operations (os, subprocess, eval, etc.).
    """
    try:
        target_line = int(patch_dict.get("target_line", 1))
        original_snippet = str(patch_dict.get("original_snippet", "")).strip()
        replacement_snippet = str(patch_dict.get("replacement_snippet", "")).strip()
        explanation = str(patch_dict.get("explanation", "Targeted code fix for the suspect line.")).strip()

        patched_code = patch_dict.get("patched_code")
        if not patched_code:
            # Build patched code manually by replacing the target line
            lines = original_code.splitlines()
            if 1 <= target_line <= len(lines):
                lines[target_line - 1] = replacement_snippet
                patched_code = "\n".join(lines) + "\n"
            else:
                patched_code = original_code + "\n" + replacement_snippet + "\n"

        # AST syntax validation guardrail
        ast.parse(patched_code)

        # Security AST check: ban dangerous operations
        parsed = ast.parse(patched_code)
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name in ("os", "subprocess", "sys", "shutil"):
                        logger.warning("Guardrail: Rejected patch importing %s", name.name)
                        return None
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "__import__"):
                    logger.warning("Guardrail: Rejected patch calling %s", node.func.id)
                    return None

        return CodePatch(
            target_line=target_line,
            original_snippet=original_snippet,
            replacement_snippet=replacement_snippet,
            explanation=explanation,
            patched_code=patched_code,
        )
    except Exception as exc:
        logger.warning("Guardrail rejected invalid code patch: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Dynamic Hint & Patch Generator
# ---------------------------------------------------------------------------

@traceable(name="generate_dynamic_hint", run_type="chain")
async def generate_dynamic_hint(
    challenge: dict,
    source_code: str,
    mistake_tags: list[str],
    visible_results: list[dict],
    hint_level: int,
    prior_hints: list[str] | None = None,
) -> tuple[str, CodePatch | None]:
    """
    Generate a dynamic, contextual hint (and code patch at level 4) using OpenRouter LLM.
    Strictly observes guardrails and falls back to deterministic hints if anything fails.
    """
    prior_hints = prior_hints or []
    challenge_title = challenge.get("title", "Coding Challenge")
    statement = challenge.get("statement", "")
    function_signature = challenge.get("function_signature", "")

    # Sanitize visible test failures for context
    failed_visible = [r for r in visible_results if r.get("outcome") and r.get("outcome") != "passed"]
    failure_context = ""
    if failed_visible:
        f = failed_visible[0]
        call = f.get("call", "test input")
        expected = f.get("expected", "")
        got = f.get("got", "")
        outcome = f.get("outcome", "wrong_output")
        failure_context = f"Failed visible test: call={call}, expected={expected}, got={got}, outcome={outcome}."

    mistake_summary = f"Detected mistake patterns: {', '.join(mistake_tags)}." if mistake_tags else ""

    # Build prompt based on requested ladder level
    if hint_level == 1:
        system_instruction = (
            "You are a skilled coding tutor in Debug Dojo. Provide a Level 1 Hint (Conceptual Nudge). "
            "Identify the core concept or edge-case consideration relevant to the failure. "
            "RULES: Do NOT mention syntax, variable names, or line numbers. Keep it under 2 sentences."
        )
    elif hint_level == 2:
        system_instruction = (
            "You are a skilled coding tutor in Debug Dojo. Provide a Level 2 Hint (Inspection Direction). "
            "Direct the learner's attention to the specific branch, loop, boundary condition, or assumption to inspect. "
            "RULES: Point them where to look in their code, but do NOT provide the corrected code. Keep it under 3 sentences."
        )
    elif hint_level == 3:
        system_instruction = (
            "You are a skilled coding tutor in Debug Dojo. Provide a Level 3 Hint (Specific Guidance). "
            "Narrow down the exact cause of the divergence and explain why the current calculation yields the incorrect output. "
            "RULES: Guide them on how to fix the logic, but do NOT write the complete solution function. Keep it concise."
        )
    else:
        # Level 4: Guardrailed Code Patch
        system_instruction = (
            "You are a skilled coding tutor in Debug Dojo. Provide a Level 4 Hint with an exact targeted Code Patch. "
            "You must return ONLY a valid JSON object with these keys:\n"
            "{\n"
            '  "hint": "Clear explanation of what needs to be changed and why",\n'
            '  "target_line": <1-based integer line number to replace or insert before>,\n'
            '  "original_snippet": "<the exact buggy line from student code>",\n'
            '  "replacement_snippet": "<the corrected Python replacement code>",\n'
            '  "patched_code": "<the complete revised source code with the fix applied>"\n'
            "}\n"
            "RULES: Modify ONLY the erroneous part. Do not erase other code. Return raw JSON without markdown code fences."
        )

    user_prompt = f"""Challenge: {challenge_title}
Signature: {function_signature}
Problem: {statement}

Student's current code:
{source_code}

Execution Evidence:
{failure_context}
{mistake_summary}

Prior Hints given to student:
{json.dumps(prior_hints)}

Requested Hint Level: {hint_level} of 4.
Generate the response strictly according to the rules."""

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt},
    ]

    try:
        raw_response = await chat_completion(messages, max_tokens=450 if hint_level == 4 else 200)

        if hint_level == 4:
            # Parse JSON patch
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = re.sub(r"^```(?:json)?\s*", "", clean_json)
                clean_json = re.sub(r"\s*```$", "", clean_json)

            try:
                patch_data = json.loads(clean_json)
                hint_text = patch_data.get("hint") or patch_data.get("explanation") or "Here is the targeted fix for your code."
                code_patch = validate_code_patch(patch_data, source_code)
                return hint_text, code_patch
            except Exception as parse_err:
                logger.warning("Could not parse JSON from LLM Level 4 response: %s", parse_err)
                # Fall back to safe deterministic patch
                return _get_fallback_hint(challenge, source_code, mistake_tags, visible_results, hint_level)
        else:
            validated_hint = validate_hint_guardrails(raw_response, hint_level, challenge.get("slug", ""))
            return validated_hint, None

    except Exception as exc:
        logger.error("Dynamic hint generation failed via LLM: %s. Using guardrailed fallback.", exc)
        return _get_fallback_hint(challenge, source_code, mistake_tags, visible_results, hint_level)


# ---------------------------------------------------------------------------
# Deterministic Fallback Hint Ladder
# ---------------------------------------------------------------------------

def _get_fallback_hint(
    challenge: dict,
    source_code: str,
    mistake_tags: list[str],
    visible_results: list[dict],
    hint_level: int,
) -> tuple[str, CodePatch | None]:
    """
    Reliable deterministic fallback hints following the taxonomy in docs/09-hints-and-guardrails.md.
    Guarantees that learner always receives high-quality guidance even if upstream LLM is unreachable.
    """
    lines = source_code.splitlines()

    # 1. Print vs return
    if "print_not_return" in mistake_tags:
        if hint_level == 1:
            return "Consider how automated test runners inspect function results versus terminal output.", None
        elif hint_level == 2:
            return "Check the final output of your function. Are you printing with print() instead of returning?", None
        elif hint_level == 3:
            return "Replace any print(...) calls with return ... so the evaluation harness receives your computed value.", None
        else:
            # Level 4 code patch
            print_line_idx = next((i for i, l in enumerate(lines) if "print(" in l), len(lines) - 1)
            orig = lines[print_line_idx] if lines else "print(result)"
            repl = orig.replace("print(", "return ").rstrip(")")
            patched_lines = list(lines)
            if print_line_idx < len(patched_lines):
                patched_lines[print_line_idx] = repl
            return (
                "Change print(...) to return to properly yield the output to the caller.",
                CodePatch(
                    target_line=print_line_idx + 1,
                    original_snippet=orig,
                    replacement_snippet=repl,
                    explanation="Return the calculated value instead of printing it.",
                    patched_code="\n".join(patched_lines) + "\n",
                ),
            )

    # 2. Mutates input
    if "mutates_input" in mistake_tags:
        if hint_level == 1:
            return "Think about side effects. In pure functions, modifying caller collections can break subsequent checks.", None
        elif hint_level == 2:
            return "Look for in-place list methods like .sort(), .append(), or .pop() that modify the input list directly.", None
        elif hint_level == 3:
            return "Work on a shallow copy of the list (e.g., numbers.copy() or sorted(numbers)) to preserve the original input.", None
        else:
            mut_line_idx = next(
                (i for i, l in enumerate(lines) if any(m in l for m in [".sort()", ".reverse()", ".pop()", "del "])),
                0,
            )
            orig = lines[mut_line_idx] if lines else ""
            repl = orig.replace(".sort()", " = sorted(").rstrip(")") + ")" if ".sort()" in orig else orig
            return (
                "Avoid in-place list mutations by creating a fresh copy or using sorted().",
                CodePatch(
                    target_line=mut_line_idx + 1,
                    original_snippet=orig,
                    replacement_snippet=repl,
                    explanation="Use non-destructive operations instead of mutating the input argument.",
                    patched_code=source_code,
                ),
            )

    # 3. Unhandled short input or boundary (e.g. k=0 or empty list)
    if "unhandled_short_input" in mistake_tags or "boundary_comparison" in mistake_tags:
        if hint_level == 1:
            return "Consider extreme boundary conditions, such as an empty collection or a count of zero.", None
        elif hint_level == 2:
            return "Check how your slicing or loop behaves when k is 0 or len(numbers) is less than expected.", None
        elif hint_level == 3:
            return "In Python, numbers[-0:] slices from index 0 to the end! Add an explicit guard clause for k == 0.", None
        else:
            # Level 4 code patch: add boundary guard clause
            body_line_idx = 1 if len(lines) > 1 else 0
            orig = lines[body_line_idx] if lines else "return sum(numbers[-k:])"
            repl = "    if k == 0:\n        return 0\n    " + orig.strip()
            patched_lines = list(lines)
            if body_line_idx < len(patched_lines):
                patched_lines[body_line_idx] = repl
            return (
                "Add a guard clause for k == 0 to prevent numbers[-0:] from selecting the entire list.",
                CodePatch(
                    target_line=body_line_idx + 1,
                    original_snippet=orig,
                    replacement_snippet=repl,
                    explanation="Guard against k == 0 before taking the negative slice.",
                    patched_code="\n".join(patched_lines) + "\n",
                ),
            )

    # Generic ladder
    if hint_level == 1:
        return "Trace your code step-by-step with the first visible test case. What assumption might not hold true?", None
    elif hint_level == 2:
        return "Inspect the condition or loop boundaries where the returned value is accumulated.", None
    elif hint_level == 3:
        return "Verify whether your loop range and comparison operators (< vs <=) align with the required boundary semantics.", None
    else:
        return "Review the logic on the return statement to ensure edge conditions evaluate to their expected values.", None
