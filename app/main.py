
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.analyzer import analyze_code
from app.schemas import CodeReviewRequest
from app.database import (
    save_review,
    get_all_reviews,
    get_review_by_id
)


app = FastAPI(
    title="CodeGuard API",
    description="Automated Code Review Assistant",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to CodeGuard API",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/api/reviews")
def create_review(request: CodeReviewRequest):
    analysis_result = analyze_code(request.code)

    review_id = str(uuid4())

    review = {
        "review_id": review_id,
        "code": request.code,
        "summary": analysis_result["summary"],
        "findings": analysis_result["findings"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    try:
        save_review(review)

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to save review: {str(error)}"
        )

    return {
        "review_id": review_id,
        "summary": analysis_result["summary"],
        "findings": analysis_result["findings"]
    }


@app.get("/api/reviews")
def list_reviews():
    try:
        reviews = get_all_reviews()
        return reviews

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve reviews: {str(error)}"
        )


@app.get("/api/reviews/{review_id}")
def review_details(review_id: str):
    try:
        review = get_review_by_id(review_id)

        if review is None:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        return review

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve review: {str(error)}"
        )
