from fastapi import APIRouter
from app.services.interviewer import ExcelInterviewAgent
from pydantic import BaseModel

router = APIRouter()
agent = ExcelInterviewAgent(max_questions=20)

class AnswerRequest(BaseModel):
    answer: str

# Get the next question
@router.get("/question")
def get_question():
    q = agent.submit_answer_and_next(answer=None)  # Starts next question or first if none submitted
    if q is None:
        return {"question": "✅ Test Completed! Click /submit_test for final summary."}
    return {"question": q}

# Submit answer & automatically move to next question
@router.post("/answer")
def post_answer(request: AnswerRequest):
    next_q = agent.submit_answer_and_next(request.answer)
    if next_q is None:
        next_q = "✅ Test Completed! Click /submit_test for final summary."
    return {
        "next_question": next_q,
        "message": "Answer recorded."
    }

# Submit test & get final summary
@router.get("/submit_test")
def submit_test():
    summary = agent.generate_summary()
    status = "✅ Test Submitted"
    return {
        "status": status,
        "summary": summary
    }
