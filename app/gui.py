import gradio as gr
from app.services.interviewer import ExcelInterviewAgent

agent = ExcelInterviewAgent()

interviewer_name = "Priya (AI Excel Interviewer)"
interviewer_avatar = "app/static/interviewer.png"

def chat(user_input, history):
    if not history:
        bot_msg = agent.get_next()
    else:
        bot_msg = agent.get_next(user_input)
    return history + [(user_input, bot_msg)], history + [(user_input, bot_msg)]

with gr.Blocks() as demo:
    gr.Markdown(f"## 👩‍💼 {interviewer_name}")
    gr.Image(interviewer_avatar, label="Your Interviewer", type="filepath", elem_id="avatar")

    chatbot = gr.Chatbot(label="Interview Transcript")
    msg = gr.Textbox(label="Your Answer:")
    clear = gr.Button("Clear Chat")

    cam = gr.Video(label="Candidate Camera Feed", source="webcam", streaming=True)

    state = gr.State([])

    def respond(message, history):
        reply, updated_history = chat(message, history)
        return updated_history, updated_history

    msg.submit(respond, [msg, state], [chatbot, state])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch(server_name="0.0.0.0", server_port=7860)
