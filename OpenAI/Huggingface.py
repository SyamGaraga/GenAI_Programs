from huggingface_hub import InferenceClient

HF_TOKEN = "enter_ur_huggingface_token_here"
client = InferenceClient("meta-llama/Meta-Llama-3.1-8B-Instruct", token=HF_TOKEN)

resp = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain vector database in one simple paragraph."}
    ],
    max_tokens=200,
    stream=False
)

print(resp.choices[0].message["content"])
