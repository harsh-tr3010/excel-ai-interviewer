import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image
import os, time, shutil
from gtts import gTTS
import pandas as pd

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

# ------------------ Instructions TTS ------------------
instructions_text = """
📢 Welcome to the AI Excel Mock Interview!  
Please **turn ON your webcam** before starting the test.  
Your video will be **recorded** for review purposes.  
Before submitting your test, **turn OFF the video recording**.  
Good luck!
"""
instructions_tts_path = "recordings/instructions.mp3"
if not os.path.exists(instructions_tts_path):
    tts = gTTS(instructions_text)
    tts.save(instructions_tts_path)

# ------------------ Timer ------------------
def get_timer_html():
    global test_started
    if not test_started or not start_time:
        return "<b>Timer: 00:00 ⏱</b>"
    elapsed = time.time() - start_time
    remaining = max(0, TIME_LIMIT - int(elapsed))
    if remaining <= 0 and test_started:
        submit_test()
        return "<b>⏰ Time is up! Test auto-submitted.</b>"
    minutes, seconds = divmod(remaining, 60)
    return f"<b>Timer: {minutes:02d}:{seconds:02d} ⏱</b>"

# ------------------ Recording Save ------------------
def save_cam_recording(video_file):
    if video_file and candidate_email:
        ext = os.path.splitext(video_file)[-1] or ".mp4"
        dest = f"recordings/{candidate_email}_cam_{int(time.time())}{ext}"
        shutil.copy(video_file, dest)
        return f"📹 Camera saved: {dest}"
    return "⚠️ No webcam recording."

# ------------------ Interview Logic ------------------
def start_interview(name, email, video_file):
    global candidate_name, candidate_email, test_started, start_time
    if not name or not email:
        return [avatar_img, "⚠️ Enter full name & email.", instructions_text, instructions_tts_path] + [gr.update(interactive=False)]*3

    master_file = "results/all_results.csv"
    if os.path.exists(master_file):
        try:
            df = pd.read_csv(master_file)
            if "candidate_email" in df.columns and email in df["candidate_email"].values:
                return [avatar_img, f"⚠️ Email '{email}' already used for test!", instructions_text, instructions_tts_path] + [gr.update(interactive=False)]*3
        except Exception:
            pass

    candidate_name, candidate_email = name, email
    q = agent.start_test()
    test_started = True
    start_time = time.time()

    save_cam_recording(video_file)

    tts_path = f"recordings/temp_{int(time.time())}.mp3"
    tts = gTTS(q)
    tts.save(tts_path)

    return [
        avatar_img,
        f"Welcome {name}! Let's begin.\n\n{q}",
        instructions_text,
        tts_path,
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
    ]

def submit_answer(answer):
    if not test_started:
        return [avatar_img, "⚠️ Test not started.", instructions_text, instructions_tts_path] + [gr.update(interactive=False)]*3

    elapsed = time.time() - (float(start_time) if start_time else 0)
    if elapsed > TIME_LIMIT:
        summary = finalize_results()
        return [avatar_img, "⏰ Time up! Auto-submitted.", summary, None] + [gr.update(interactive=False)]*3

    result = agent.evaluate_and_store(answer)
    if "error" in result:
        return [avatar_img, "⚠️ No active question.", "", None] + [gr.update(interactive=False)]*3

    feedback = result['result']['feedback']
    next_q = result.get("next_question")

    if next_q:
        tts_path = f"recordings/temp_{int(time.time())}.mp3"
        tts = gTTS(next_q)
        tts.save(tts_path)
        return [
            avatar_img,
            next_q,
            f"Your Answer: {answer}\n\nFeedback: {feedback}",
            tts_path,
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
            None,
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
        ]

def next_question(answer):
    return submit_answer(answer)

def finalize_results():
    global test_started
    summary = agent.generate_summary(candidate_name, candidate_email)
    filename, master_file = agent.save_results_to_csv(candidate_name, candidate_email)
    total_correct = sum(a["score"] for a in agent.answers)
    result_status = "✅ PASS" if total_correct >= 15 else "❌ FAIL"
    final_summary = f"{summary}\nFinal Result: {result_status} ({total_correct}/20)\n\nSaved: {filename}\nMaster: {master_file}"

    save_cam_recording(cam_record.value)
    test_started = False
    return final_summary

def submit_test():
    save_cam_recording(cam_record.value)  # auto-save on submit
    summary = finalize_results()
    return [
        avatar_img,
        "✅ Test Submitted",
        summary,
        None,
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    ]

# ------------------ Build Interface ------------------
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer with Webcam & TTS")

    # Top section: Instructions + TTS + Webcam
    with gr.Row():
        with gr.Column(scale=3):
            instructions_label = gr.Markdown(f"**{instructions_text}**")
            tts_audio = gr.Audio(
                value=instructions_tts_path,
                autoplay=True,
                interactive=False,
                visible=True,
                label="📢 Instructions (Autoplay)"
            )
        with gr.Column(scale=1):
            cam_record = gr.Video(label="Webcam", height=200, interactive=True)

    # Name & Email
    with gr.Row():
        name_box = gr.Textbox(label="Full Name")
        email_box = gr.Textbox(label="Email")

    start_btn = gr.Button("🎬 Start Test (20 Questions)")

    # Avatar & question
    with gr.Row():
        avatar = gr.Image(avatar_img, interactive=False)
        question_label = gr.Textbox(label="Question", value="Fill details then Start Test", interactive=False)

    answer_input = gr.Textbox(label="Your Answer")

    # Buttons
    with gr.Row():
        submit_btn = gr.Button("Submit Answer", interactive=False)
        next_btn = gr.Button("➡️ Next Question", interactive=False)
        submit_test_btn = gr.Button("Submit Test", interactive=False)

    # Feedback & Timer
    with gr.Row():
        feedback_label = gr.Textbox(label="Feedback / Summary", interactive=False, lines=10)
        timer_html = gr.HTML("<b>Timer: 00:00 ⏱</b>")

    # ------------------ Auto-repeat Instructions TTS ------------------
    def repeat_instructions():
        if not test_started:
            return instructions_tts_path
        return gr.update()  # stop once test starts

    instructions_timer = gr.Timer(20)
    instructions_timer.tick(fn=repeat_instructions, outputs=[tts_audio])

    # ------------------ Wiring ------------------
    start_btn.click(fn=start_interview, inputs=[name_box, email_box, cam_record],
                    outputs=[avatar, question_label, instructions_label, tts_audio,
                             submit_btn, next_btn, submit_test_btn, cam_record])

    submit_btn.click(fn=submit_answer, inputs=[answer_input],
                     outputs=[avatar, question_label, instructions_label, tts_audio,
                              submit_btn, next_btn, submit_test_btn, cam_record])

    next_btn.click(fn=next_question, inputs=[answer_input],
                   outputs=[avatar, question_label, instructions_label, tts_audio,
                            submit_btn, next_btn, submit_test_btn, cam_record])

    submit_test_btn.click(fn=submit_test, inputs=[],
                          outputs=[avatar, question_label, instructions_label, tts_audio,
                                   submit_btn, next_btn, submit_test_btn, cam_record])

    # Timer for test countdown
    gr.Timer(1).tick(fn=get_timer_html, outputs=[timer_html])

demo.launch()
