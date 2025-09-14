import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image
import os
from datetime import datetime
import shutil
import csv

# Initialize interviewer
agent = ExcelInterviewAgent()

# Avatar
avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((150, 150))

# Directories
recordings_dir = "recordings"
results_dir = "results"
os.makedirs(recordings_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

results_file = os.path.join(results_dir, "interview_results.csv")

# Create results file with header if not exists
if not os.path.exists(results_file):
    with open(results_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Candidate Name", "Timestamp", "Question", "Answer", "Score", "Feedback", "Video Path", "Summary"])

# Greeting
intro_text = "👋 Hello Candidate! Welcome to your AI Excel Interview.\n\nEnter your name below and press **Start Test**. Recording will begin automatically and continue until the last question."

# --- Logic functions ---

def start_test(name):
    """Start the interview and begin recording"""
    if not name.strip():
        return avatar_img, "⚠️ Please enter your name before starting.", "Enter your name first.", gr.update(visible=True)

    agent.reset()
    q = agent.get_next_question()
    return avatar_img, q, f"Recording started for {name}. Please answer the questions one by one.", gr.update(visible=True)


def submit_answer(name, answer, video_file):
    """Process each answer and move to next question"""
    result = agent.evaluate_answer(answer)
    q = agent.get_next_question()

    if q:
        feedback = f"Score: {result['score']} | {result['feedback']}"

        # Log each Q/A immediately
        with open(results_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), agent.questions[agent.current_index-1], answer, result["score"], result["feedback"], "", ""])

        return avatar_img, q, feedback, None
    else:
        # End of interview → stop & save video automatically
        summary = agent.generate_summary()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = name.replace(" ", "_") if name else "candidate"
        save_path = os.path.join(recordings_dir, f"{safe_name}_{ts}_interview_session.webm")

        if video_file and os.path.exists(video_file):
            shutil.move(video_file, save_path)
            save_status = f"✅ Interview finished for {name}!\n📂 Recording saved at {save_path}"
        else:
            save_status = f"⚠️ Interview finished for {name}, but no recording file received."
            save_path = "N/A"

        # Save final summary row in CSV
        with open(results_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "END", "N/A", "N/A", "N/A", save_path, summary])

        return avatar_img, "✅ Interview finished!", summary, save_status


# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer")
    gr.Markdown(intro_text)

    candidate_name = gr.Textbox(label="Candidate Name", placeholder="Enter your full name")

    with gr.Row():
        avatar = gr.Image(avatar_img, interactive=False)
        question_label = gr.Textbox(label="Question", value="Press Start to begin interview", interactive=False)

    answer_input = gr.Textbox(label="Your Answer")

    # Continuous recording input (video + audio together)
    video_input = gr.Video(label="Recording (continuous)", source="webcam")

    with gr.Row():
        start_btn = gr.Button("▶️ Start Test")
        submit_btn = gr.Button("Submit Answer")

    feedback_label = gr.Textbox(label="Feedback / Summary", interactive=False)
    save_status = gr.Textbox(label="Save Status", interactive=False)

    # Events
    start_btn.click(fn=start_test, inputs=[candidate_name], outputs=[avatar, question_label, feedback_label, video_input])
    submit_btn.click(fn=submit_answer, inputs=[candidate_name, answer_input, video_input], outputs=[avatar, question_label, feedback_label, save_status])

demo.launch()
