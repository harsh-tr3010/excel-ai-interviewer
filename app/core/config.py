import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Excel Mock Interviewer"
    OPENAI_API_KEY: str = os.getenv("Saloni", "")

settings = Settings()
