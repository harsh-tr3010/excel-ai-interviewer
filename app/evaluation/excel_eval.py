import difflib

class ExcelEvaluator:
    def evaluate(self, answer: str, expected: str) -> dict:
        """
        Simple similarity check between candidate answer and expected answer.
        """
        ratio = difflib.SequenceMatcher(None, answer.lower(), expected.lower()).ratio()
        feedback = "Good understanding" if ratio > 0.7 else "Needs improvement"
        return {
            "score": round(ratio * 100, 2),
            "feedback": feedback
        }
