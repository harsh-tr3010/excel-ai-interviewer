import gradio as gr
from app.services.interviewer import ExcelInterviewAgent
from PIL import Image

# Initialize the interview agent
agent = ExcelInterviewAgent()

# Load avatar image
avatar_path = "app/static/interviewer.png"
avatar_img = Image.open(avatar_path).resize((150, 150))

# Function to get next question
def ask_question():
    q = agent.get_next_question()
    if q:
        return avatar_img, q, ""
    else:
        return avatar_img, "Interview finished!", ""

# Function to submit answer and get feedback
def submit_answer(answer):
    result = agent.evaluate_answer(answer)
    return avatar_img, agent.current_question["Question"], f"Score: {result['score']} | {result['feedback']}"

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI Excel Mock Interviewer")

    with gr.Row():
        avatar = gr.Image(avatar_img, elem_id="avatar", interactive=False)
        question_label = gr.Textbox(label="Question", value="Click 'Next Question' to start", interactive=False)
    
    answer_input = gr.Textbox(label="Your Answer")
    
    with gr.Row():
        next_btn = gr.Button("Next Question")
        submit_btn = gr.Button("Submit Answer")
    
    feedback_label = gr.Textbox(label="Feedback", interactive=False)
    
    next_btn.click(fn=ask_question, outputs=[avatar, question_label, feedback_label])
    submit_btn.click(fn=submit_answer, inputs=[answer_input], outputs=[avatar, question_label, feedback_label])

# Launch Gradio app
demo.launch()
