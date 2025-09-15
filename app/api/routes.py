from fastapi import APIRouter, HTTPException
from app.services.interviewer import ExcelInterviewAgent
import pandas as pd
import os

router = APIRouter()
agent = ExcelInterviewAgent()

RESULTS_FILE = "results/all_results.csv"


@router.post("/start")
def start_test(candidate_name: str, candidate_email: str):
    # Prevent duplicate email attempts
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        if candidate_email in df["candidate_email"].values:
            raise HTTPException(
                status_code=400,
                detail=f"❌ Candidate with email {candidate_email} has already taken the test."
            )

    q = agent.start_test()
    return {"message": f"Welcome {candidate_name}!", "question": q}


@router.get("/question")
def get_question():
    q = agent.get_next_question()
    return {"question": q}


@router.post("/answer")
def post_answer(answer: str):
    return agent.evaluate_and_store(answer)


@router.post("/submit")
def submit_test(candidate_name: str, candidate_email: str):
    summary = agent.generate_summary(candidate_name, candidate_email)
    file_path, master_file = agent.save_results_to_csv(candidate_name, candidate_email)

    # Extract pass/fail status
    df = pd.read_csv(file_path)
    final_result = df["final_result"].iloc[0]
    final_score = df["final_score"].iloc[0]

    return {
        "summary": summary,
        "final_result": final_result,
        "final_score": final_score,
        "file_saved": file_path,
        "master_file": master_file
    }
