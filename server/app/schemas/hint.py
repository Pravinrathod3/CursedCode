from pydantic import BaseModel, Field


class HintRequest(BaseModel):
    submission_id: str = Field(..., min_length=1, max_length=128)


class HintResponse(BaseModel):
    submission_id: str
    hint_index: int
    hint: str
