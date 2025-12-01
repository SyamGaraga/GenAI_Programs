import gradio as gr

def greet(name, is_morning):
    if is_morning:
        return f"Good morning, {name}!"
    else:
        return f"Hello, {name}!"
    
demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Your name"),
        gr.Checkbox(label="Is it morning?")
    ],
    outputs=gr.Textbox(label="Greeting"),
    title="Greeting App"
)

if __name__ == "__main__":
    demo.launch(inbrowser = True)