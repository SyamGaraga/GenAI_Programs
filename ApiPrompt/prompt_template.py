from huggingface_hub import InferenceClient

HF_TOKEN = "ener_your_huggingface_api_token_heres"

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_TOKEN
)

TEMPLATE = "You are a {role}.\nExplain the topic for a beginner.\nTopic: {topic}"

def explain_topic(topic, role="Cricket Analyst"):
    prompt = TEMPLATE.format(role=role, topic=topic)

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "Follow the template strictly."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message["content"]


print(explain_topic("Vector Database"))
