from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.interviewer import ExcelInterviewAgent
import pandas as pd
import os
import shutil
import time

router = APIRouter()
agent = ExcelInterviewAgent()

RESULTS_FILE = "results/all_results.csv"

# Keep track of in-progress tests
active_candidates = set()


@router.post("/start")
def start_test(candidate_name: str = Form(...), candidate_email: str = Form(...)):
    """
    Start the test for a candidate.
    Auto-starts webcam on frontend (handled by client-side JS/Gradio),
    and returns first question and instructions TTS file path.
    """
    # Check if already completed in CSV (case insensitive)
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        if candidate_email.lower() in df["candidate_email"].astype(str).str.lower().values:
            raise HTTPException(
                status_code=400,
                detail=f"❌ Candidate with email {candidate_email} has already taken the test."
            )

    # Check if already active
    if candidate_email in active_candidates:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Candidate with email {candidate_email} is already taking the test."
        )

    # Mark as active
    active_candidates.add(candidate_email)

    # Start interview
    first_question = agent.start_test()

    # Instructions text & TTS generation
    instructions_text = (
        "Welcome to the AI Excel Mock Interview! "
        "Please allow camera access when prompted. "
        "Your video will start recording automatically. "
        "Recording will stop when you submit your test. Good luck!"
    )
    try:
        from gtts import gTTS
        tts_path = f"results/recordings/instructions_{int(time.time())}.mp3"
        tts = gTTS(instructions_text)
        os.makedirs("results/recordings", exist_ok=True)
        tts.save(tts_path)
    except Exception:
        tts_path = None

    return {
        "message": f"Welcome {candidate_name}!",
        "instructions": instructions_text,
        "instructions_tts": tts_path,
        "question": first_question
    }


@router.get("/question")
def get_question():
    """
    Return next question in the test.
    """
    q = agent.get_next_question()
    return {"question": q}


@router.post("/answer")
def post_answer(answer: str = Form(...)):
    """
    Submit answer for current question and get feedback.
    """
    return agent.evaluate_and_store(answer)


@router.post("/submit")
async def submit_test(
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    recording: UploadFile = File(None)  # optional webcam recording
):
    """
    Submit entire test for candidate.
    Saves Excel results & recording automatically.
    """
    # Ensure candidate started
    if candidate_email not in active_candidates:
        raise HTTPException(
            status_code=400,
            detail="❌ Candidate not registered for this test session."
        )

    # Generate summary and save CSV
    try:
        summary = agent.generate_summary(candidate_name, candidate_email)
        file_path, master_file = agent.save_results_to_csv(candidate_name, candidate_email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save recording if provided
    recording_path = None
    if recording:
        os.makedirs("results/recordings", exist_ok=True)
        timestamp = int(time.time())
        ext = os.path.splitext(recording.filename)[1] or ".mp4"
        recording_path = f"results/recordings/{candidate_name}_{candidate_email}_{timestamp}{ext}"
        with open(recording_path, "wb") as buffer:
            shutil.copyfileobj(recording.file, buffer)

    # Remove from active candidates
    active_candidates.remove(candidate_email)

    # Extract final score & status
    df = pd.read_csv(file_path)
    final_result = df["final_result"].iloc[0]
    final_score = df["total_correct"].iloc[0]

    return {
        "summary": summary,
        "final_result": final_result,
        "final_score": final_score,
        "file_saved": file_path,
        "master_file": master_file,
        "recording_saved": recording_path if recording else "No recording uploaded"
    }
