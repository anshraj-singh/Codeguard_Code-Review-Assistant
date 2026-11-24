
from pydantic import BaseModel, Field


class CodeReviewRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        description="Python code that needs to be analyzed"
    )


class Finding(BaseModel):
    line: int
    severity: str
    rule: str
    message: str


class ReviewSummary(BaseModel):
    total_issues: int
    high: int
    medium: int
    low: int


class CodeReviewResponse(BaseModel):
    review_id: str
    summary: ReviewSummary
    findings: list[Finding]


class ReviewHistoryItem(BaseModel):
    review_id: str
    total_issues: int
    high: int
    medium: int
    low: int
