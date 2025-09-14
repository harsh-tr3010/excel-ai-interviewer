import pandas as pd
import random
from app.evaluation.excel_eval import ExcelEvaluator

class ExcelInterviewAgent:
    def __init__(self, question_file="data/excel_questions.xlsx"):
        self.questions = pd.read_excel(question_file)
        self.current_question = None
        self.evaluator = ExcelEvaluator()
        self.asked = []
        self.answers = []  # store user answers

    def get_next_question(self):
        available = self.questions[~self.questions.index.isin(self.asked)]
        if available.empty:
            return None
        q = available.sample(1).iloc[0]
        self.current_question = q
        self.asked.append(q.name)
        return q["Question"]

    def evaluate_answer(self, answer: str):
        if self.current_question is None:
            return {"error": "No active question"}
        expected = self.current_question["ExpectedAnswer"]
        result = self.evaluator.evaluate(answer, str(expected))
        # Store answer and feedback
        self.answers.append({
            "question": self.current_question["Question"],
            "user_answer": answer,
            "score": result["score"],
            "feedback": result["feedback"]
        })
        return result

    def generate_summary(self):
        if not self.answers:
            return "No answers recorded."
        total_score = sum(a["score"] for a in self.answers)
        avg_score = round(total_score / len(self.answers), 2)
        summary = f"Interview Summary:\nTotal Questions: {len(self.answers)}\nAverage Score: {avg_score}\n\nDetails:\n"
        for a in self.answers:
            summary += f"Q: {a['question']}\nYour Answer: {a['user_answer']}\nScore: {a['score']} | {a['feedback']}\n\n"
        return summary
