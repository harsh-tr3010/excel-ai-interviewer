from fastapi import APIRouter
from app.services.interviewer import ExcelInterviewAgent

router = APIRouter()
agent = ExcelInterviewAgent()

@router.get("/start")
def start_interview():
    return {"message": agent.get_next()}

@router.post("/answer")
def answer_interview(answer: str):
    return {"message": agent.get_next(answer)}

@router.get("/summary")
def get_summary():
    return {"feedback": agent.get_next()}
