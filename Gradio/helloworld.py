import gradio as gr

# 1. Normal Python function
def greet(name):
    return f"Hello, {name}!"

# 2. Wrap it in a Gradio Interface
demo = gr.Interface(
    fn=greet,          # function to run
    inputs="text",     # what input UI to show
    outputs="text",    # what output UI to show
    title="Hello Gradio",
    description="Type your name and click Submit."
)

# 3. Launch the app
if __name__ == "__main__":
    demo.launch(inbrowser=True)