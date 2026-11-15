import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")

client = InferenceClient(
    base_url="http://127.0.0.1:11434/v1",
    api_key="local ollama :)"
)

output = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[
        {"role": "user", "content": "My name is"},
    ],
    stream=False,
    max_tokens=1024,
    extra_body={'thinking': {'type': 'disabled'}},
)

print(output.choices[0].message.content)