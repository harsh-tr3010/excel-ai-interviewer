import pandas as pd
from app.evaluation.excel_eval import ExcelEvaluator

class ExcelInterviewAgent:
    def __init__(self, question_file="data/excel_questions.xlsx", max_questions=20):
        self.questions = pd.read_excel(question_file)
        self.evaluator = ExcelEvaluator()
        self.max_questions = max_questions
        self.asked = []
        self.answers = {}  # store answers with question index
        self.current_index = -1  # index in asked list

        # Initialize question order
        self.question_order = list(self.questions.index)
        if len(self.question_order) > max_questions:
            import random
            self.question_order = random.sample(self.question_order, max_questions)

    def get_question_by_index(self, idx):
        if idx < 0 or idx >= len(self.question_order):
            return None
        q_idx = self.question_order[idx]
        q_row = self.questions.loc[q_idx]
        return f"Question {idx+1}/{self.max_questions}: {q_row['Question']}"

    def next_question(self, answer=None):
        # Store previous answer if any
        if self.current_index >= 0 and answer is not None:
            q_idx = self.question_order[self.current_index]
            expected = self.questions.loc[q_idx]["ExpectedAnswer"]
            if not answer.strip():
                user_answer = "No Answer"
                score, feedback = 0, "No answer provided."
            else:
                res = self.evaluator.evaluate(answer, str(expected))
                score = res["score"]
                feedback = res["feedback"]
                if score == 0:
                    feedback = f"Wrong answer. Correct answer: {expected}"
                user_answer = answer
            self.answers[q_idx] = {"user_answer": user_answer, "score": score, "feedback": feedback}

        # Move to next question
        if self.current_index + 1 >= len(self.question_order):
            return None
        self.current_index += 1
        return self.get_question_by_index(self.current_index)

    def prev_question(self):
        if self.current_index <= 0:
            return None
        self.current_index -= 1
        return self.get_question_by_index(self.current_index)

    def get_current_answer(self):
        if self.current_index < 0:
            return ""
        q_idx = self.question_order[self.current_index]
        return self.answers.get(q_idx, {}).get("user_answer", "")

    def generate_summary(self, candidate_name=None, candidate_email=None):
        total_score = sum(a["score"] for a in self.answers.values())
        avg_score = round(total_score / self.max_questions, 2)
        summary = "Interview Summary:\n"
        if candidate_name and candidate_email:
            summary += f"Candidate: {candidate_name} ({candidate_email})\n"
        summary += f"Total Questions: {len(self.question_order)}/{self.max_questions}\n"
        summary += f"Average Score: {avg_score}\n\nDetails:\n"
        for idx in self.question_order:
            q_text = self.questions.loc[idx]["Question"]
            ans = self.answers.get(idx, {"user_answer": "No Answer", "score": 0, "feedback": "Not answered"})
            summary += f"Q: {q_text}\nYour Answer: {ans['user_answer']}\nScore: {ans['score']} | {ans['feedback']}\n\n"
        return summary
