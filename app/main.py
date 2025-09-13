from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="AI Excel Mock Interviewer")

app.include_router(routes.router)

@app.get("/")
def root():
    return {"message": "AI-Powered Excel Mock Interviewer is running 🚀"}
