import gradio as gr

def analyze_text(text):
    text = text.strip()
    num_chars = len(text)
    num_words = len(text.split()) if text else 0
    
    summary = (
        f"Characters: {num_chars}\n"
        f"Words: {num_words}\n"
    )
    # You can add more logic here later (sentiment, keywords, etc.)
    return summary

demo = gr.Interface(
    fn=analyze_text,
    inputs=gr.Textbox(
        lines=4,
        label="Enter some text"
    ),
    outputs=gr.Textbox(
        label="Analysis"
    ),
    title="Simple Text Analyzer",
    description="Counts characters and words. You can replace the function with any ML model later."
)

if __name__ == "__main__":
    demo.launch(inbrowser = True)