"""Router for FAQ query and knowledge-base endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.faq_service import get_all_faqs, resolve_faq

router = APIRouter(prefix="/faq", tags=["faq"])


class FaqQueryRequest(BaseModel):
    question: str


class FaqQueryResponse(BaseModel):
    question: str
    answer: str | None
    confidence: float | None
    matched: bool


@router.get("", summary="List all FAQs from the business knowledge base")
async def list_faqs() -> list[dict]:
    """Return every FAQ entry configured in business_config.yaml."""
    return get_all_faqs()


@router.post("/query", response_model=FaqQueryResponse)
async def query_faq(payload: FaqQueryRequest) -> FaqQueryResponse:
    """Find the best FAQ answer for a given question string."""
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    result = resolve_faq(payload.question)
    if result:
        return FaqQueryResponse(
            question=payload.question,
            answer=result["answer"],
            confidence=result["confidence"],
            matched=True,
        )
    return FaqQueryResponse(
        question=payload.question,
        answer=None,
        confidence=None,
        matched=False,
    )
