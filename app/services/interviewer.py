import pandas as pd
import os
from app.evaluation.excel_eval import ExcelEvaluator

class ExcelInterviewAgent:
    def __init__(self, question_file="data/excel_questions.csv", max_questions=20):
        self.questions = pd.read_csv(question_file)
        self.current_question = None
        self.evaluator = ExcelEvaluator()
        self.asked = []
        self.answers = []  # store user answers
        self.max_questions = max_questions

    def start_test(self):
        """Reset state and start test from first question."""
        self.current_question = None
        self.asked = []
        self.answers = []
        return self.get_next_question()

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

    def evaluate_and_store(self, answer: str):
        """Evaluate and store answer as Correct/Wrong based on threshold (50)."""
        if self.current_question is None:
            return {"error": "No active question."}

        expected = self.current_question["ExpectedAnswer"]

        if not answer or str(answer).strip() == "":
            result = {"score": 0, "feedback": "No answer provided. Marked as Wrong."}
            user_answer = "No Answer"
        else:
            raw_result = self.evaluator.evaluate(answer, str(expected))
            user_answer = answer
            if raw_result["score"] < 50:
                result = {"score": 0, "feedback": f"Wrong. Correct answer: {expected}"}
            else:
                result = {"score": 1, "feedback": "Correct"}

        self.answers.append({
            "question": self.current_question["Question"],
            "user_answer": user_answer,
            "expected": expected,
            "score": result["score"],
            "feedback": result["feedback"]
        })

        next_q = self.get_next_question()
        return {"result": result, "next_question": next_q}

    def generate_summary(self, candidate_name=None, candidate_email=None):
        total_correct = sum(a["score"] for a in self.answers)
        result_status = "PASS" if total_correct >= 15 else "FAIL"

        summary = "Interview Summary:\n"
        if candidate_name and candidate_email:
            summary += f"Candidate: {candidate_name} ({candidate_email})\n"
        summary += f"Total Questions Answered: {len(self.answers)}/{self.max_questions}\n"
        summary += f"Correct Answers: {total_correct}\n"
        summary += f"Final Result: {result_status} ({total_correct}/{self.max_questions})\n\nDetails:\n"

        for a in self.answers:
            summary += f"Q: {a['question']}\nYour Answer: {a['user_answer']}\n"
            summary += f"Expected: {a['expected']}\n"
            summary += f"Result: {'Correct' if a['score']==1 else 'Wrong'}\n"
            summary += f"Feedback: {a['feedback']}\n\n"

        return summary

    def save_results_to_csv(self, candidate_name=None, candidate_email=None):
        os.makedirs("results", exist_ok=True)
        master_file = "results/all_results.csv"

        # Prevent duplicate emails
        if os.path.exists(master_file):
            master_df = pd.read_csv(master_file)
            if candidate_email in master_df["candidate_email"].values:
                raise ValueError(f"Email '{candidate_email}' already exists! Cannot save results.")

        total_correct = sum(a["score"] for a in self.answers)
        result_status = "PASS" if total_correct >= 15 else "FAIL"

        filename = f"results/{candidate_name or 'candidate'}_results.csv"
        df = pd.DataFrame(self.answers)
        df["candidate_name"] = candidate_name
        df["candidate_email"] = candidate_email
        df["total_correct"] = total_correct
        df["final_result"] = result_status
        df.to_csv(filename, index=False)

        # Append to master file
        if os.path.exists(master_file):
            df.to_csv(master_file, mode="a", header=False, index=False)
        else:
            df.to_csv(master_file, index=False)

        return filename, master_file
