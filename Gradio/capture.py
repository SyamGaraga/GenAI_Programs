import gradio as gr
from PIL import Image
import numpy as np
from tensorflow.keras.applications import (
    mobilenet_v2,
    resnet50,
    imagenet_utils
)

# Load models once
mobilenet_model = mobilenet_v2.MobileNetV2(weights="imagenet")
resnet_model = resnet50.ResNet50(weights="imagenet")

def classify_image(img, model_choice):
    if img is None:
        return "Please upload an image."

    img = Image.fromarray(img).convert("RGB")

    # Choose model
    if model_choice == "MobileNetV2":
        model = mobilenet_model
        preprocess = mobilenet_v2.preprocess_input
        size = (224, 224)

    elif model_choice == "ResNet50":
        model = resnet_model
        preprocess = resnet50.preprocess_input
        size = (224, 224)

    # Preprocess
    x = img.resize(size)
    x = np.array(x).astype("float32")
    x = np.expand_dims(x, axis=0)
    x = preprocess(x)

    # Predict
    preds = model.predict(x)
    decoded = imagenet_utils.decode_predictions(preds, top=3)[0]

    # Format output
    result = ""
    for i, (_, label, prob) in enumerate(decoded, start=1):
        result += f"{i}. {label} — {prob*100:.2f}%\n"
    return result


# Gradio UI
demo = gr.Interface(
    fn=classify_image,
    inputs=[
        gr.Image(type="numpy"),
        gr.Radio(["MobileNetV2", "ResNet50"], label="Choose Model")
    ],
    outputs=gr.Text(label="Predictions"),
    title="Image Classification using Gradio",
    description="Upload an image and choose a model to classify it."
)

demo.launch(inbrowser=True)
