def parse_feedback(raw_feedback: str):
    """Convert LLM feedback into structured dictionary (basic PoC)"""
    feedback = {"scores": {}, "strengths": [], "improvements": []}

    for line in raw_feedback.splitlines():
        if "Score" in line:
            try:
                q, score = line.split(":", 1)
                feedback["scores"][q.strip()] = score.strip()
            except:
                continue
        elif "Strength" in line:
            feedback["strengths"].append(line.strip())
        elif "Improve" in line:
            feedback["improvements"].append(line.strip())

    return feedback
