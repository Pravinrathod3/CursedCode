from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal


class SubmitRequest(BaseModel):
    learner_id: str = Field(..., min_length=1, max_length=128)
    challenge_id: str = Field(..., min_length=1, max_length=128)
    code: str = Field(default="")

    @field_validator("code")
    @classmethod
    def code_size(cls, v: str) -> str:
        from app.core.config import get_settings
        limit = get_settings().max_code_bytes
        if len(v.encode()) > limit:
            raise ValueError(f"Code exceeds {limit} bytes.")
        return v


class VisibleResult(BaseModel):
    test: int
    call: str | None = None
    expected: str | None = None
    got: str | None = None
    outcome: Literal["passed", "wrong_output", "runtime_error", "timeout"]


class HiddenResult(BaseModel):
    test: int
    outcome: Literal["passed", "wrong_output", "runtime_error", "timeout"]


class SubmitResponse(BaseModel):
    submission_id: str
    learner_id: str
    challenge_id: str
    visible: list[VisibleResult]
    hidden: list[HiddenResult]
    mistake_tags: list[str] = []
    explanation: str | None = None
    limit: str | None = None
