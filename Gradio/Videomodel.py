import gradio as gr
import cv2
import numpy as np
import librosa # <--- NEW IMPORT FOR AUDIO FIX
from PIL import Image
from transformers import pipeline

# --- TensorFlow Imports for Image Classification ---
from tensorflow.keras.applications import mobilenet_v2, resnet50, imagenet_utils

print("--- INITIALIZING AI MODELS ---")

# 1. LOAD IMAGE IDENTIFICATION MODELS
print("Loading Vision Models...")
mobilenet_model = mobilenet_v2.MobileNetV2(weights="imagenet")
resnet_model = resnet50.ResNet50(weights="imagenet")

# 2. LOAD AUDIO MODEL
print("Loading Audio Model...")
# We add explicit device=-1 to ensure it uses CPU if GPU isn't available to prevent CUDA errors
audio_pipe = pipeline("audio-classification", model="mit/ast-finetuned-audioset-10-10-0.4593")

# 3. LOAD VIDEO EXPLANATION MODEL
print("Loading Captioning Model...")
caption_pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

print("--- MODELS READY ---")


# ==========================================
# PROCESSING FUNCTIONS
# ==========================================

def identify_image_objects(img_array, model_choice):
    if img_array is None:
        return "Please upload an image."

    img = Image.fromarray(img_array).convert("RGB")

    if model_choice == "MobileNetV2":
        model = mobilenet_model
        preprocess = mobilenet_v2.preprocess_input
        size = (224, 224)
    else:
        model = resnet_model
        preprocess = resnet50.preprocess_input
        size = (224, 224)

    x = img.resize(size)
    x = np.array(x).astype("float32")
    x = np.expand_dims(x, axis=0)
    x = preprocess(x)

    preds = model.predict(x)
    decoded = imagenet_utils.decode_predictions(preds, top=3)[0]

    result = "Detected Objects:\n"
    for i, (_, label, prob) in enumerate(decoded, start=1):
        result += f"{i}. {label} — {prob*100:.2f}%\n"
    return result

def identify_sound_clip(audio_filepath):
    """ 
    UPDATED FUNCTION: Uses librosa to fix sampling rate errors 
    """
    if audio_filepath is None:
        return "Please record audio first."
    
    try:
        # 1. Load and resample audio to 16000Hz (Required by this specific AI model)
        # Using librosa handles the conversion from standard mic input to AI input safely
        audio_data, sample_rate = librosa.load(audio_filepath, sr=16000)
        
        # 2. Pass the numpy array directly to the pipeline
        # This bypasses file format issues (wav vs mp3 vs flac)
        preds = audio_pipe(audio_data)
        
        # 3. Format Output
        result = "Sound identification:\n"
        for p in preds[:3]: # Top 3
             result += f"- {p['label']} ({p['score']*100:.1f}%)\n"
        return result
        
    except Exception as e:
        return f"Error processing audio: {str(e)}\n\nTry installing: pip install torchaudio librosa"

def explain_video_scene(video_path):
    if video_path is None:
        return "Please upload a video."
    
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Jump to middle
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "Could not read video file."
        
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    result = caption_pipe(pil_image)
    return result[0]['generated_text']


# ==========================================
# GRADIO UI
# ==========================================

with gr.Blocks(title="Multi-Modal AI Tool", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 All-in-One AI Analyzer")
    
    with gr.Tabs():
        # TAB 1: IMAGE
        with gr.TabItem("🖼️ Identify Image"):
            with gr.Row():
                with gr.Column():
                    img_input = gr.Image(type="numpy", label="Upload Image")
                    model_sel = gr.Radio(["MobileNetV2", "ResNet50"], value="MobileNetV2", label="Model")
                    img_btn = gr.Button("Identify", variant="primary")
                with gr.Column():
                    img_output = gr.Textbox(label="Results")
            img_btn.click(identify_image_objects, inputs=[img_input, model_sel], outputs=img_output)

        # TAB 2: AUDIO
        with gr.TabItem("🎤 Identify Sound"):
            gr.Markdown("Record a sound (clapping, dog barking, keys jingling).")
            with gr.Row():
                 with gr.Column():
                    # Sources=["microphone"] enables the record button
                    audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record")
                    audio_btn = gr.Button("Identify Sound", variant="primary")
                 with gr.Column():
                    audio_output = gr.Textbox(label="AI Result")
            audio_btn.click(identify_sound_clip, inputs=audio_input, outputs=audio_output)

        # TAB 3: VIDEO
        with gr.TabItem("🎬 Explain Video"):
            with gr.Row():
                with gr.Column():
                    video_input = gr.Video(label="Upload Video")
                    video_btn = gr.Button("Explain", variant="primary")
                with gr.Column():
                    video_output = gr.Textbox(label="Description")
            video_btn.click(explain_video_scene, inputs=video_input, outputs=video_output)

if __name__ == "__main__":
    demo.launch(inbrowser=True)