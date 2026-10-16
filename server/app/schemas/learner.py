from pydantic import BaseModel
from typing import Any


class RecurringMistake(BaseModel):
    category: str
    challenge_count: int


class ConceptMastery(BaseModel):
    concept: str
    estimate: float
    score: float = 0.0
    grade: str = "Grade 4"
    difficulty: str = "Easy"


class NextChallenge(BaseModel):
    challenge_id: str
    title: str = ""
    grade: str = "Grade 4"
    difficulty: str = "Easy"
    reason: str


class LearnerResponse(BaseModel):
    learner_id: str
    recurring_mistakes: list[RecurringMistake] = []
    mastery: list[ConceptMastery] = []
    next_challenge: NextChallenge | None = None
