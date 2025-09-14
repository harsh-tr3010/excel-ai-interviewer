import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image

agent = ExcelInterviewAgent(max_questions=20)

avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((150, 150))

candidate_name = None
candidate_email = None

# Start Test
def start_interview(name, email):
    global candidate_name, candidate_email
    candidate_name, candidate_email = name, email
    q = agent.submit_answer_and_next(answer=None)  # Start first question
    return avatar_img, q, "", ""  # answer box cleared

# Submit Answer → stores and moves to next automatically
def submit_answer(answer):
    next_q = agent.submit_answer_and_next(answer)
    feedback = ""
    if next_q is None:
        next_q = "✅ Test Completed! Click Submit Test for final summary."
    return avatar_img, next_q, "", feedback  # answer box cleared

# Submit Test → final summary
def submit_test():
    summary = agent.generate_summary(candidate_name, candidate_email)
    status = "✅ Test Submitted"
    return avatar_img, status, "", summary

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer")

    # Candidate info
    with gr.Row():
        name_box = gr.Textbox(label="Full Name", placeholder="Enter your name")
        email_box = gr.Textbox(label="Email", placeholder="Enter your email")

    start_btn = gr.Button("🎬 Start Test (20 Questions)")

    with gr.Row():
        avatar = gr.Image(avatar_img, interactive=False)
        question_label = gr.Textbox(label="Question", value="Fill name & email, then click Start Test.", interactive=False)
        answer_input = gr.Textbox(label="Your Answer")

    with gr.Row():
        submit_btn = gr.Button("Submit Answer")
        submit_test_btn = gr.Button("Submit Test")

    feedback_label = gr.Textbox(label="Feedback / Summary", interactive=False)

    # Wiring
    start_btn.click(fn=start_interview, inputs=[name_box, email_box],
                    outputs=[avatar, question_label, answer_input, feedback_label])
    submit_btn.click(fn=submit_answer, inputs=[answer_input],
                     outputs=[avatar, question_label, answer_input, feedback_label])
    submit_test_btn.click(fn=submit_test, inputs=[],
                          outputs=[avatar, question_label, answer_input, feedback_label])

demo.launch()
