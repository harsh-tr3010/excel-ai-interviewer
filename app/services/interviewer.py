import pandas as pd
import random
from openai import OpenAI
from app.core.config import settings

class ExcelInterviewAgent:
    def __init__(self):
        # Load question bank from Excel
        df = pd.read_excel("data/excel_questions.xlsx")
        self.questions = df["Question"].tolist()
        random.shuffle(self.questions)

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.state = {
            "stage": "intro",
            "current_index": 0,
            "answers": []
        }

    def get_next(self, user_input=None):
        if self.state["stage"] == "intro":
            self.state["stage"] = "questions"
            return "👋 Hello! I’m your AI Excel Interviewer. Let’s start!\n\n" + self.questions[0]

        if self.state["stage"] == "questions":
            if user_input:
                self.state["answers"].append(user_input)
                self.state["current_index"] += 1

            if self.state["current_index"] < len(self.questions):
                return self.questions[self.state["current_index"]]
            else:
                self.state["stage"] = "summary"
                return "✅ That’s the end of the interview. Preparing your feedback..."

        if self.state["stage"] == "summary":
            return self.evaluate()

    def evaluate(self):
        eval_prompt = "You are an Excel interviewer. Evaluate the candidate's responses:\n\n"
        for q, a in zip(self.questions, self.state["answers"]):
            eval_prompt += f"Q: {q}\nA: {a}\n\n"
        eval_prompt += "Provide detailed feedback, scores (1-5), strengths, and improvements."

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert Excel interviewer."},
                      {"role": "user", "content": eval_prompt}]
        )
        return response.choices[0].message.content
