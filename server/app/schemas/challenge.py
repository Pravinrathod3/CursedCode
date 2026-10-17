from pydantic import BaseModel, Field
from typing import Any


class VisibleTestCase(BaseModel):
    test: int
    call: str
    expected: str


class ExampleCase(BaseModel):
    call: str
    expected: str
    explanation: str | None = None


class ChallengeListItem(BaseModel):
    id: str
    slug: str
    title: str
    description: str = ""
    grade: str = "Grade 4"
    difficulty: str = "Easy"
    tags: list[str] = []
    status: str = "New"
    estimatedTime: str = "10 min"
    sort_order: int = 0
    time_limit_ms: int | None = None
    input_constraints: str | None = None
    time_complexity: str | None = None


class ChallengeDetail(ChallengeListItem):
    statement: str
    function_signature: str = ""
    starter_code: str = ""
    starterCode: str = ""
    example: ExampleCase | None = None
    visibleTests: list[VisibleTestCase] = []
    hiddenTestCount: int = 5
    constraints: dict | None = None
