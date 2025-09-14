import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image

agent = ExcelInterviewAgent(max_questions=20)

avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((150, 150))

candidate_name = None
candidate_email = None

def start_interview(name, email):
    global candidate_name, candidate_email
    candidate_name, candidate_email = name, email
    q = agent.next_question()
    answer = agent.get_current_answer()
    return avatar_img, q, answer, ""

def submit_answer(answer):
    next_q = agent.next_question(answer)
    current_answer = agent.get_current_answer()
    feedback = ""
    if next_q is None:
        feedback = agent.generate_summary(candidate_name, candidate_email)
        next_q = "✅ Test Completed!"
    return avatar_img, next_q, current_answer, feedback

def prev_question():
    prev_q = agent.prev_question()
    current_answer = agent.get_current_answer()
    feedback = ""
    if prev_q is None:
        prev_q = "This is the first question."
    return avatar_img, prev_q, current_answer, feedback

def submit_test():
    summary = agent.generate_summary(candidate_name, candidate_email)
    status = "✅ Test Submitted" if len(agent.answers) >= agent.max_questions else "Test not completed yet"
    return avatar_img, status, "", summary

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer")

    with gr.Row():
        name_box = gr.Textbox(label="Full Name", placeholder="Enter your name")
        email_box = gr.Textbox(label="Email", placeholder="Enter your email")

    start_btn = gr.Button("🎬 Start Test (20 Questions)")

    with gr.Row():
        avatar = gr.Image(avatar_img, interactive=False)
        question_label = gr.Textbox(label="Question", value="Fill name & email, then click Start Test.", interactive=False)
        answer_input = gr.Textbox(label="Your Answer")

    with gr.Row():
        prev_btn = gr.Button("Previous Question")
        submit_btn = gr.Button("Submit Answer")
        submit_test_btn = gr.Button("Submit Test")

    feedback_label = gr.Textbox(label="Feedback / Summary", interactive=False)

    start_btn.click(fn=start_interview, inputs=[name_box, email_box],
                    outputs=[avatar, question_label, answer_input, feedback_label])
    submit_btn.click(fn=submit_answer, inputs=[answer_input],
                     outputs=[avatar, question_label, answer_input, feedback_label])
    prev_btn.click(fn=prev_question, inputs=[],
                   outputs=[avatar, question_label, answer_input, feedback_label])
    submit_test_btn.click(fn=submit_test, inputs=[],
                          outputs=[avatar, question_label, answer_input, feedback_label])

demo.launch()
