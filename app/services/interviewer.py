from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ExcelInterviewAgent:
    def __init__(self):
        self.state = {
            "stage": "intro",
            "questions": [
                "Can you explain the difference between VLOOKUP and INDEX-MATCH in Excel?",
                "How would you clean and preprocess raw sales data with missing values?",
                "Write a formula to calculate Year-to-Date sales dynamically.",
                "How do you use Pivot Tables to summarize multi-dimensional data?",
                "Explain how you would create a dashboard with slicers and charts in Excel."
            ],
            "current_index": 0,
            "history": [],
            "answers": []
        }

    def get_next(self, user_input=None):
        """Handles interview state transitions"""
        if self.state["stage"] == "intro":
            self.state["stage"] = "questions"
            return "Hello, I am your AI Excel Interviewer. Let’s begin! " + self.state["questions"][0]

        if self.state["stage"] == "questions":
            if user_input:
                self.state["answers"].append(user_input)
                self.state["current_index"] += 1

            if self.state["current_index"] < len(self.state["questions"]):
                return self.state["questions"][self.state["current_index"]]
            else:
                self.state["stage"] = "summary"
                return "Thank you! Let me prepare your evaluation report..."

        if self.state["stage"] == "summary":
            return self.evaluate()

    def evaluate(self):
        """Send candidate answers to LLM for scoring"""
        eval_prompt = "You are an Excel interviewer. Evaluate the candidate's responses:\n\n"
        for q, a in zip(self.state["questions"], self.state["answers"]):
            eval_prompt += f"Q: {q}\nA: {a}\n\n"

        eval_prompt += "Provide feedback with scores (1-5) for each answer, strengths, and areas to improve."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert Excel interviewer."},
                      {"role": "user", "content": eval_prompt}]
        )
        return response.choices[0].message.content
