import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image
import os
from datetime import datetime
import shutil

# Initialize interviewer
agent = ExcelInterviewAgent()

# Avatar
avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((150, 150))

# Recordings directory
recordings_dir = "recordings"
os.makedirs(recordings_dir, exist_ok=True)

# Greeting
intro_text = "👋 Hello Candidate! Welcome to your AI Excel Interview.\n\nOnce you press **Start Test**, recording will begin automatically and continue until the last question."

# --- Logic functions ---

def start_test():
    """Start the interview and begin recording"""
    agent.reset()
    q = agent.get_next_question()
    return avatar_img, q, "Recording started. Please answer the questions one by one.", gr.update(visible=True)

def submit_answer(answer, video_file):
    """Process each answer and move to next question"""
    result = agent.evaluate_answer(answer)
    q = agent.get_next_question()

    if q:
        feedback = f"Score: {result['score']} | {result['feedback']}"
        return avatar_img, q, feedback, None
    else:
        # End of interview → stop & save video automatically
        summary = agent.generate_summary()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(recordings_dir, f"{ts}_interview_session.webm")

        if video_file and os.path.exists(video_file):
            shutil.move(video_file, save_path)
            save_status = f"✅ Interview finished!\n📂 Recording saved at {save_path}"
        else:
            save_status = "⚠️ Interview finished, but no recording file received."

        return avatar_img, "✅ Interview finished!", summary, save_status

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer")
    gr.Markdown(intro_text)

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
    start_btn.click(fn=start_test, inputs=[], outputs=[avatar, question_label, feedback_label, video_input])
    submit_btn.click(fn=submit_answer, inputs=[answer_input, video_input], outputs=[avatar, question_label, feedback_label, save_status])

demo.launch()
