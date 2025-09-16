import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image
import os, time, shutil
from gtts import gTTS
import pandas as pd
import glob

# ------------------ Initialization ------------------
agent = ExcelInterviewAgent(max_questions=20)

avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((250, 250))

candidate_name = None
candidate_email = None
test_started = False
start_time = None
TIME_LIMIT = 300  # 5 minutes

os.makedirs("recordings", exist_ok=True)

# ------------------ Helper to create TTS ------------------
def make_tts(text: str, prefix="temp"):
    for old in glob.glob("recordings/temp_*.mp3"):
        try:
            os.remove(old)
        except:
            pass
    path = f"recordings/{prefix}_{int(time.time())}.mp3"
    tts = gTTS(text)
    tts.save(path)
    return path

# ------------------ Instructions TTS ------------------
instructions_text = """
Welcome to the AI Excel Mock Interview!  
Please allow camera access when prompted.  
Your video will start recording automatically.  
Recording will stop when you submit your test.  
Good luck!
"""
instructions_tts_path = make_tts(instructions_text, prefix="instructions")

# ------------------ Timer ------------------
def get_timer_html():
    global test_started
    if not test_started or not start_time:
        return "<b>Timer: 00:00 ⏱</b>"
    elapsed = time.time() - start_time
    remaining = max(0, TIME_LIMIT - int(elapsed))
    if remaining <= 0 and test_started:
        return auto_submit()
    minutes, seconds = divmod(remaining, 60)
    return f"<b>Timer: {minutes:02d}:{seconds:02d} ⏱</b>"

# ------------------ Recording Save ------------------
def save_cam_recording(video_file):
    """Save uploaded webcam video into recordings/ only."""
    if video_file and candidate_email:
        ext = os.path.splitext(video_file)[-1] or ".mp4"
        dest = f"recordings/{candidate_email}_cam_{int(time.time())}{ext}"
        try:
            shutil.copy(video_file, dest)
        except Exception:
            shutil.move(video_file, dest)
        return f"📹 Camera saved: {dest}"
    return "⚠️ No webcam recording."

# ------------------ Interview Logic ------------------
def start_interview(name, email, video_file):
    global candidate_name, candidate_email, test_started, start_time
    if not name or not email:
        return [avatar_img, "⚠️ Enter full name & email.", instructions_text, instructions_tts_path,
                gr.update(value="⚠️ Enter details before starting", interactive=False),
                gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)]

    master_file = "results/all_results.csv"
    if os.path.exists(master_file):
        try:
            df = pd.read_csv(master_file)
            if "candidate_email" in df.columns and email.strip().lower() in df["candidate_email"].astype(str).str.lower().values:
                return [avatar_img, "⚠️ This email has already been used for a test!", instructions_text, instructions_tts_path,
                        gr.update(value="Duplicate email detected ❌", interactive=False),
                        gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)]
        except Exception:
            pass

    candidate_name, candidate_email = name, email
    q = agent.start_test()
    test_started = True
    start_time = time.time()

    # Auto-save first chunk of recording if available
    save_cam_recording(video_file)
    tts_path = make_tts(q, prefix="question")

    return [
        avatar_img,
        q,
        instructions_text,
        tts_path,
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
    ]

def submit_answer(answer):
    if not test_started:
        return [avatar_img, "⚠️ Test not started.", instructions_text, instructions_tts_path,
                gr.update(value="⚠️ Test not started", interactive=False),
                gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)]

    elapsed = time.time() - (float(start_time) if start_time else 0)
    if elapsed > TIME_LIMIT:
        return auto_submit()

    result = agent.evaluate_and_store(answer)
    if "error" in result:
        return [avatar_img, "⚠️ No active question.", instructions_text, None,
                gr.update(value="⚠️ No active question", interactive=False),
                gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)]

    feedback = result['result']['feedback']
    next_q = result.get("next_question")

    if next_q:
        tts_path = make_tts(next_q, prefix="question")
        return [
            avatar_img,
            next_q,
            instructions_text,
            tts_path,
            gr.update(value=f"Answer: {answer}\n\nFeedback: {feedback}", interactive=True),
            gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),
        ]
    else:
        return auto_submit()

def next_question(answer):
    return submit_answer(answer)

def finalize_results():
    global test_started
    summary = agent.generate_summary(candidate_name, candidate_email)
    filename, master_file = agent.save_results_to_csv(candidate_name, candidate_email)
    total_correct = sum(a["score"] for a in agent.answers)
    result_status = "✅ PASS" if total_correct >= 15 else "❌ FAIL"
    final_summary = f"{summary}\n\nFinal Result: {result_status} ({total_correct}/20)\nSaved: {filename}\nMaster File: {master_file}"

    # Save the final webcam recording
    save_cam_recording(cam_record.value)
    test_started = False
    return final_summary

def auto_submit():
    summary = finalize_results()
    return [avatar_img, "⏰ Time Up! Test Auto-Submitted.", instructions_text, None,
            gr.update(value=summary, interactive=False),
            gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)]

def submit_test():
    summary = finalize_results()
    return [avatar_img, "✅ Test Submitted", instructions_text, None,
            gr.update(value=summary, interactive=False),
            gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)]

# ------------------ Build Interface ------------------
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer with Webcam & TTS")

    with gr.Row():
        with gr.Column(scale=3):
            instructions_label = gr.Markdown(f"**{instructions_text}**")
            tts_audio = gr.Audio(value=instructions_tts_path, autoplay=True, interactive=False,
                                 visible=True, label="📢 Instructions & Questions (Autoplay)")
        with gr.Column(scale=1):
            # Enable auto-record from webcam
            cam_record = gr.Video(label="Webcam (Recording Auto-Starts)", height=200, sources=["webcam"])

    with gr.Row():
        name_box = gr.Textbox(label="Full Name")
        email_box = gr.Textbox(label="Email")

    start_btn = gr.Button("🎬 Start Test (20 Questions)")

    with gr.Row():
        avatar = gr.Image(avatar_img, interactive=False)
        question_label = gr.Textbox(label="Question", value="Fill details then Start Test", interactive=False)

    answer_input = gr.Textbox(label="Your Answer")

    with gr.Row():
        submit_btn = gr.Button("Submit Answer", interactive=False)
        next_btn = gr.Button("➡️ Next Question", interactive=False)
        submit_test_btn = gr.Button("Submit Test", interactive=False)

    with gr.Row():
        feedback_label = gr.Textbox(label="Feedback / Summary", interactive=False, lines=10)
        timer_html = gr.HTML("<b>Timer: 00:00 ⏱</b>")

    def repeat_instructions():
        if not test_started:
            return instructions_tts_path
        return gr.update()

    gr.Timer(20).tick(fn=repeat_instructions, outputs=[tts_audio])
    gr.Timer(1).tick(fn=get_timer_html, outputs=[timer_html])

    start_btn.click(fn=start_interview, inputs=[name_box, email_box, cam_record],
                    outputs=[avatar, question_label, instructions_label, tts_audio,
                             feedback_label, submit_btn, next_btn, submit_test_btn])

    submit_btn.click(fn=submit_answer, inputs=[answer_input],
                     outputs=[avatar, question_label, instructions_label, tts_audio,
                              feedback_label, submit_btn, next_btn, submit_test_btn])

    next_btn.click(fn=next_question, inputs=[answer_input],
                   outputs=[avatar, question_label, instructions_label, tts_audio,
                            feedback_label, submit_btn, next_btn, submit_test_btn])

    submit_test_btn.click(fn=submit_test, inputs=[],
                          outputs=[avatar, question_label, instructions_label, tts_audio,
                                   feedback_label, submit_btn, next_btn, submit_test_btn])

demo.launch(share=True)
