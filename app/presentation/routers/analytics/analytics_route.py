from fastapi import APIRouter

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/overview")
def analytics_overview():
    return {
        "total_conversations": 125,
        "active_users": 18,
        "total_documents": 42,
        "unanswered_queries": 7,
        "total_messages": 3840,
        "avg_response_time": "1.2 sec"
    }

# Conversation analytics
@router.get("/conversations")
def conversations():
    return {
        "today": 35,
        "this_week": 220,
        "this_month": 840,
    }

# Document analytics
@router.get("/documents")
def documents():
    return {
        "uploaded": 120,
        "processed": 115,
        "failed": 5,
    }