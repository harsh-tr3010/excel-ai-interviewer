from fastapi import APIRouter
from app.services.interviewer import ExcelInterviewAgent

router = APIRouter()
agent = ExcelInterviewAgent()

@router.get("/question")
def get_question():
    q = agent.get_next_question()
    return {"question": q}

@router.post("/answer")
def post_answer(answer: str):
    return agent.evaluate_answer(answer)
