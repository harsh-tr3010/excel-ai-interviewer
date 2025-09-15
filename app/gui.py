import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image
import os, time, shutil
import pandas as pd

# Initialize agent
agent = ExcelInterviewAgent(max_questions=20)

# Avatar
avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((250, 250))

# Candidate session
candidate_name = None
candidate_email = None
test_started = False
start_time = None
TIME_LIMIT = 300  # 5 minutes

# Intro
intro_text = """👋 Hello! I am your AI Excel Interviewer.  
The test has **20 questions**, **5 minutes limit**, and **surveillance enabled**.  
📢 **You must also spell out your answer aloud while typing it.**  
"""

# Create recordings folder
os.makedirs("recordings", exist_ok=True)

# --- Utility ---
def email_exists(email):
    master_file = "results/all_results.csv"
    if os.path.exists(master_file):
        try:
            df = pd.read_csv(master_file)
            return email in df["candidate_email"].values
        except Exception:
            return False
    return False

# --- Save recordings ---
def save_mic_recording(audio_file):
    if audio_file and candidate_email:
        ext = os.path.splitext(audio_file)[-1] or ".wav"
        dest = f"recordings/{candidate_email}_mic_{int(time.time())}{ext}"
        shutil.copy(audio_file, dest)
        return dest
    return None

def save_cam_recording(video_file):
    if video_file and candidate_email:
        ext = os.path.splitext(video_file)[-1] or ".mp4"
        dest = f"recordings/{candidate_email}_cam_{int(time.time())}{ext}"
        shutil.copy(video_file, dest)
        return dest
    return None

# --- Timer ---
def get_timer_html():
    global test_started
    if not test_started or not start_time:
        return "<b>Timer: 00:00 ⏱</b>"
    elapsed = time.time() - start_time
    remaining = max(0, TIME_LIMIT - int(elapsed))
    minutes, seconds = divmod(remaining, 60)
    if remaining <= 0 and test_started:
        submit_test()  # auto-submit
        return "<b>⏰ Time is up! Test auto-submitted.</b>"
    return f"<b>Timer: {minutes:02d}:{seconds:02d} ⏱</b>"

# --- Interview Logic ---
def start_interview(name, email):
    global candidate_name, candidate_email, test_started, start_time
    if not name or not email:
        return [avatar_img, "⚠️ Enter full name & email.", "", "", 
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False)]
    
    if email_exists(email):
        return [avatar_img, "⚠️ Email already used for test!", "", "", 
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False)]
    
    candidate_name, candidate_email = name, email
    q = agent.start_test()
    test_started = True
    start_time = time.time()

    return [
        avatar_img,
        f"Welcome {name}! Let's begin.\n\n{q}",
        "",
        "",
        gr.update(interactive=True),  # submit
        gr.update(interactive=True),  # next
        gr.update(interactive=True),  # submit test
        gr.update(interactive=True),  # mic
        gr.update(interactive=True),  # cam
    ]

def submit_answer(answer):
    if not test_started:
        return [avatar_img, "⚠️ Test not started.", "", "", 
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False)]
    
    elapsed = time.time() - (start_time or 0)
    if elapsed > TIME_LIMIT:
        summary = finalize_results()
        return [avatar_img, "⏰ Time up! Auto-submitted.", summary, "", 
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False)]
    
    result = agent.evaluate_and_store(answer)
    if "error" in result:
        return [avatar_img, "⚠️ No active question.", "", "", 
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False), gr.update(interactive=False),
                gr.update(interactive=False)]
    
    feedback = result['result']['feedback']
    next_q = result.get("next_question")
    
    if next_q:
        return [
            avatar_img,
            next_q,
            feedback,
            "",
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
        ]
    else:
        summary = finalize_results()
        return [
            avatar_img,
            "✅ Test Completed!",
            summary,
            "",
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
        ]

def next_question(answer):
    return submit_answer(answer)

# --- Finalize and save recordings ---
def finalize_results():
    global test_started
    summary = agent.generate_summary(candidate_name, candidate_email)
    filename, master_file = agent.save_results_to_csv(candidate_name, candidate_email)

    total_correct = sum(a["score"] for a in agent.answers)
    result_status = "✅ PASS" if total_correct >= 15 else "❌ FAIL"
    final_summary = f"{summary}\nFinal Result: {result_status} ({total_correct}/20)\n\nSaved: {filename}\nMaster: {master_file}"
    
    # Save surveillance
    save_mic_recording(mic_record.value)
    save_cam_recording(cam_record.value)
    
    test_started = False
    return final_summary

def submit_test():
    summary = finalize_results()
    return [
        avatar_img,
        "✅ Test Submitted",
        summary,
        "",
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    ]

# --- Build Interface ---
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer with Voice & Surveillance")
    gr.Markdown(intro_text)

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

    mic_record = gr.Audio(label="Mic Surveillance", interactive=True)
    cam_record = gr.Video(label="Webcam Surveillance", interactive=True)
    start_ts_hidden = gr.Textbox(value="", visible=False)

    # Wiring
    start_btn.click(start_interview, inputs=[name_box, email_box],
                    outputs=[avatar, question_label, feedback_label,
                             start_ts_hidden, submit_btn,
                             next_btn, submit_test_btn, mic_record, cam_record])

    submit_btn.click(submit_answer, inputs=[answer_input],
                     outputs=[avatar, question_label, feedback_label,
                              start_ts_hidden, submit_btn,
                              next_btn, submit_test_btn, mic_record, cam_record])

    next_btn.click(next_question, inputs=[answer_input],
                    outputs=[avatar, question_label, feedback_label,
                             start_ts_hidden, submit_btn,
                             next_btn, submit_test_btn, mic_record, cam_record])

    submit_test_btn.click(submit_test, inputs=[],
                          outputs=[avatar, question_label, feedback_label,
                                   start_ts_hidden, submit_btn,
                                   next_btn, submit_test_btn, mic_record, cam_record])

    # Timer runs every second
    gr.Timer(1).tick(fn=get_timer_html, outputs=[timer_html])

demo.launch()
