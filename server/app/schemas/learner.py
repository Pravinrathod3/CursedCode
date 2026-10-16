from pydantic import BaseModel


class RecurringMistake(BaseModel):
    category: str
    challenge_count: int


class ConceptMastery(BaseModel):
    concept: str
    estimate: float


class NextChallenge(BaseModel):
    challenge_id: str
    reason: str


class LearnerResponse(BaseModel):
    learner_id: str
    recurring_mistakes: list[RecurringMistake]
    mastery: list[ConceptMastery]
    next_challenge: NextChallenge | None = None
