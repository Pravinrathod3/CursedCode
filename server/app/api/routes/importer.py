"""
Sheet Importer and AI Test Case Ingestion Routes.
Allows importing popular sheets (Striver's A2Z, CP-31) or custom problems,
generating comprehensive visible tests and hidden edge cases via OpenRouter.
"""
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.integrations.supabase_client import get_supabase
from app.services.testcase_generator import generate_testcases_for_problem
from app.data.curated_sheets import CURATED_SHEETS
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/importer", tags=["importer"])


class GenerateTestsRequest(BaseModel):
    title: str = Field(..., min_length=2)
    statement: str = Field(..., min_length=5)
    function_signature: str = ""
    starter_code: str = ""
    difficulty: str = "Medium"
    tags: list[str] = []


class TestCaseItem(BaseModel):
    test: int | None = None
    call: str
    expected: str
    description: str = ""
    visibility: str = "visible"  # 'visible' | 'hidden'


class ImportProblemRequest(BaseModel):
    id: str | None = None
    slug: str | None = None
    title: str
    statement: str
    function_signature: str = ""
    starter_code: str = ""
    difficulty: str = "Medium"
    grade: str = "Grade 3"
    tags: list[str] = []
    estimated_time: str = "15 min"
    auto_generate_tests: bool = True
    visible_tests: list[TestCaseItem] = []
    hidden_tests: list[TestCaseItem] = []
    hints: list[str] = []


class BatchImportRequest(BaseModel):
    sheet_id: str
    problem_ids: list[str] = []
    auto_generate_tests: bool = True


@router.get("/sheets")
async def get_curated_sheets():
    """Return available pre-configured competitive programming & DSA sheets."""
    overview = []
    for sheet_id, sheet in CURATED_SHEETS.items():
        overview.append({
            "id": sheet_id,
            "name": sheet["name"],
            "description": sheet["description"],
            "badge": sheet["badge"],
            "categories": sheet["categories"],
            "problem_count": len(sheet["problems"]),
            "problems": [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "difficulty": p["difficulty"],
                    "category": p.get("category", ""),
                    "tags": p.get("tags", []),
                    "statement": p.get("statement", ""),
                    "function_signature": p.get("function_signature", ""),
                    "starter_code": p.get("starter_code", ""),
                    "example": p.get("example", None),
                }
                for p in sheet["problems"]
            ]
        })
    return overview


@router.post("/generate-tests")
async def generate_tests_endpoint(body: GenerateTestsRequest):
    """Generate visible test cases and hidden edge cases using OpenRouter LLM."""
    try:
        generated = await generate_testcases_for_problem(
            title=body.title,
            statement=body.statement,
            function_signature=body.function_signature,
            starter_code=body.starter_code,
            difficulty=body.difficulty,
            tags=body.tags
        )
        return generated
    except Exception as exc:
        logger.error("Failed to generate test cases: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


def _save_problem_to_db(db, problem_data: dict, visible_tests: list, hidden_tests: list, hints: list) -> dict:
    """Helper to persist or update challenge, test_cases, and hints in DB."""
    slug = problem_data.get("slug") or problem_data.get("id") or str(uuid.uuid4())[:8]
    slug = slug.strip().lower().replace(" ", "-").replace("_", "-")

    # Map difficulty to database enum
    diff_val = problem_data.get("difficulty", "Medium").lower()
    if "hard" in diff_val:
        db_diff = "advanced"
    elif "easy" in diff_val:
        db_diff = "beginner"
    else:
        db_diff = "intermediate"

    # Check if challenge exists by slug
    existing = db.table("challenges").select("id").eq("slug", slug).execute()
    c_uuid = None
    if existing.data:
        c_uuid = existing.data[0]["id"]
        db.table("challenges").update({
            "title": problem_data["title"],
            "statement": problem_data["statement"],
            "function_signature": problem_data.get("function_signature", ""),
            "starter_code": problem_data.get("starter_code", ""),
            "difficulty": db_diff,
            "is_published": True,
        }).eq("id", c_uuid).execute()
    else:
        c_uuid = str(uuid.uuid4())
        db.table("challenges").insert({
            "id": c_uuid,
            "slug": slug,
            "title": problem_data["title"],
            "statement": problem_data["statement"],
            "function_signature": problem_data.get("function_signature", ""),
            "starter_code": problem_data.get("starter_code", ""),
            "difficulty": db_diff,
            "language": "python",
            "is_published": True,
            "sort_order": 50,
        }).execute()

    # Clear old test results (foreign key to test_cases) then old test cases
    try:
        existing_tc = (
            db.table("test_cases")
            .select("id")
            .eq("challenge_id", c_uuid)
            .execute()
        )
        tc_ids = [row["id"] for row in (existing_tc.data or [])]
        if tc_ids:
            db.table("test_results").delete().in_("test_case_id", tc_ids).execute()
    except Exception:
        pass

    # Clear old test cases for this challenge
    try:
        db.table("test_cases").delete().eq("challenge_id", c_uuid).execute()
    except Exception:
        pass

    # Insert visible test cases
    db_tests = []
    for i, vt in enumerate(visible_tests, start=1):
        call_str = vt.get("call") or ""
        db_tests.append({
            "id": str(uuid.uuid4()),
            "challenge_id": c_uuid,
            "visibility": "visible",
            "ordinal": i,
            "input_payload": {"call": call_str},
            "expected_output": vt.get("expected", ""),
            "description": vt.get("description") or f"Visible test {i}",
            "timeout_ms": 1500,
        })

    # Insert hidden edge cases
    for j, ht in enumerate(hidden_tests, start=len(visible_tests) + 1):
        call_str = ht.get("call") or ""
        db_tests.append({
            "id": str(uuid.uuid4()),
            "challenge_id": c_uuid,
            "visibility": "hidden",
            "ordinal": j,
            "input_payload": {"call": call_str},
            "expected_output": ht.get("expected", ""),
            "description": ht.get("description") or f"Edge case {j}",
            "timeout_ms": 1500,
        })

    if db_tests:
        db.table("test_cases").insert(db_tests).execute()

    # Clear and insert hints if available
    try:
        db.table("challenge_hints").delete().eq("challenge_id", c_uuid).execute()
    except Exception:
        pass

    db_hints = []
    for h_idx, h_text in enumerate(hints[:4], start=1):
        db_hints.append({
            "id": str(uuid.uuid4()),
            "challenge_id": c_uuid,
            "hint_level": h_idx,
            "hint_text": h_text,
        })
    if db_hints:
        try:
            db.table("challenge_hints").insert(db_hints).execute()
        except Exception as e:
            logger.warning("Could not persist hints: %s", e)

    return {
        "id": slug,
        "uuid": c_uuid,
        "slug": slug,
        "title": problem_data["title"],
        "visible_test_count": len(visible_tests),
        "hidden_test_count": len(hidden_tests),
        "hints_count": len(hints),
    }


@router.post("/import-problem")
async def import_single_problem(body: ImportProblemRequest, db=Depends(get_supabase)):
    """Import or create a challenge, generating edge cases with OpenRouter if requested."""
    visible = [vt.model_dump() for vt in body.visible_tests]
    hidden = [ht.model_dump() for ht in body.hidden_tests]
    hints = list(body.hints)

    # If test cases were not provided or auto-generation is enabled, generate via OpenRouter
    if body.auto_generate_tests and (len(visible) < 2 or len(hidden) < 3):
        generated = await generate_testcases_for_problem(
            title=body.title,
            statement=body.statement,
            function_signature=body.function_signature,
            starter_code=body.starter_code,
            difficulty=body.difficulty,
            tags=body.tags
        )
        if not visible:
            visible = generated.get("visible_tests", [])
        if not hidden:
            hidden = generated.get("hidden_tests", [])
        if not hints:
            hints = generated.get("hints", [])

    saved = _save_problem_to_db(
        db=db,
        problem_data=body.model_dump(),
        visible_tests=visible,
        hidden_tests=hidden,
        hints=hints
    )
    return saved


@router.post("/batch-import")
async def batch_import_sheet(body: BatchImportRequest, db=Depends(get_supabase)):
    """Batch import selected problems from a curated sheet with OpenRouter edge cases."""
    sheet = CURATED_SHEETS.get(body.sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail=f"Sheet '{body.sheet_id}' not found.")

    problems_to_import = []
    if body.problem_ids:
        target_ids = set(body.problem_ids)
        problems_to_import = [p for p in sheet["problems"] if p["id"] in target_ids]
    else:
        problems_to_import = sheet["problems"]

    results = []
    for p in problems_to_import:
        visible = []
        hidden = []
        hints = []

        if body.auto_generate_tests:
            try:
                gen = await generate_testcases_for_problem(
                    title=p["title"],
                    statement=p["statement"],
                    function_signature=p.get("function_signature", ""),
                    starter_code=p.get("starter_code", ""),
                    difficulty=p.get("difficulty", "Medium"),
                    tags=p.get("tags", [])
                )
                visible = gen.get("visible_tests", [])
                hidden = gen.get("hidden_tests", [])
                hints = gen.get("hints", [])
            except Exception as e:
                logger.warning("Error generating tests for %s: %s", p['title'], e)

        # Baseline fallback if needed
        if not visible and p.get("example"):
            visible = [
                {"test": 1, "call": p["example"]["call"], "expected": p["example"]["expected"], "description": "Example 1", "visibility": "visible"}
            ]

        res = _save_problem_to_db(db, p, visible, hidden, hints)
        results.append(res)

    return {
        "sheet_id": body.sheet_id,
        "sheet_name": sheet["name"],
        "imported_count": len(results),
        "challenges": results,
    }
