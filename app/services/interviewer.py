import pandas as pd
from app.evaluation.excel_eval import ExcelEvaluator

class ExcelInterviewAgent:
    def __init__(self, question_file="data/excel_questions.xlsx", max_questions=20):
        self.questions = pd.read_excel(question_file)
        self.questions.columns = [c.strip() for c in self.questions.columns]
        required_cols = ['Question', 'ExpectedAnswer']
        for col in required_cols:
            if col not in self.questions.columns:
                raise ValueError(f"Missing required column in Excel file: '{col}'")
        self.current_question = None
        self.evaluator = ExcelEvaluator()
        self.asked = []
        self.answers = []
        self.max_questions = max_questions

    def get_next_question(self):
        if len(self.asked) >= self.max_questions:
            self.current_question = None
            return None

        available = self.questions[~self.questions.index.isin(self.asked)]
        if available.empty:
            self.current_question = None
            return None

        q = available.sample(1).iloc[0]
        self.current_question = q
        self.asked.append(q.name)
        return f"Question {len(self.asked)}/{self.max_questions}: {q['Question']}"

    def submit_answer_and_next(self, answer: str):
        if self.current_question is None:
            return {"error": "No active question. Either test not started or completed."}

        expected = str(self.current_question.get("ExpectedAnswer", "")).strip()
        if not answer or str(answer).strip() == "":
            result = {"score": 0, "feedback": "No answer provided. Marked as wrong."}
            user_answer = "No Answer"
        else:
            result = self.evaluator.evaluate(answer, expected)
            user_answer = answer
            if result["score"] == 0:
                result["feedback"] = f"Wrong answer. Correct answer: {expected}"

        self.answers.append({
            "question": self.current_question["Question"],
            "user_answer": user_answer,
            "score": result["score"],
            "feedback": result["feedback"]
        })

        # Get next question automatically
        next_q = self.get_next_question()
        return {"result": result, "next_question": next_q}

    def generate_summary(self, candidate_name=None, candidate_email=None):
        if len(self.answers) < self.max_questions:
            return f"Test not completed yet. Questions answered: {len(self.answers)}/{self.max_questions}"

        total_score = sum(a["score"] for a in self.answers)
        avg_score = round(total_score / len(self.answers), 2)

        summary = "Interview Summary:\n"
        if candidate_name and candidate_email:
            summary += f"Candidate: {candidate_name} ({candidate_email})\n"
        summary += f"Total Questions Asked: {len(self.answers)}/{self.max_questions}\n"
        summary += f"Average Score: {avg_score}\n\nDetails:\n"

        for a in self.answers:
            summary += f"Q: {a['question']}\nYour Answer: {a['user_answer']}\n"
            summary += f"Score: {a['score']} | {a['feedback']}\n\n"

        return summary
