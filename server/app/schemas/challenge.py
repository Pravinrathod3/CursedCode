from pydantic import BaseModel, Field
from typing import Literal
import uuid


class ChallengeListItem(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    sort_order: int


class ChallengeDetail(ChallengeListItem):
    statement: str
    function_signature: str
    starter_code: str
