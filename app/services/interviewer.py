import pandas as pd
import random
from app.evaluation.excel_eval import ExcelEvaluator

class ExcelInterviewAgent:
    def __init__(self, question_file="data/excel_questions.xlsx"):
        self.questions = pd.read_excel(question_file)
        self.current_question = None
        self.evaluator = ExcelEvaluator()
        self.asked = []

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
        return self.evaluator.evaluate(answer, str(expected))
