import os
from huggingface_hub import InferenceClient
import random
import json
import re

HF_TOKEN = os.environ.get("HF_TOKEN")

client = InferenceClient(
    base_url="http://127.0.0.1:11434/v1",
    api_key="local ollama :)"
)

def get_weather(location:str) -> str:
    temperature = random.randint(-5, 35)
    return f"The weather in {location} is {temperature}°C"

def calculate_shipping_sla(distance_km:int) -> str:
    if distance_km > 15:
        minutes = 40
    elif distance_km > 10:
        minutes = 30
    elif distance_km > 5:
        minutes = 20
    elif distance_km > 0:
        minutes = 10
    else:
        return "invalid distance_km value"
    
    return f"Your package will arrive in {minutes} minutes"

AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "calculate_shipping_sla": calculate_shipping_sla,
}

SYSTEM_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

get_weather: Get the current weather in a given location
calculate_shipping_sla: Calculate the estimated time of arrival based on a distance

The way you use the tools is by specifying a json blob.
Specifically, this json should have an `action` key (with the name of the tool to use) and an `action_input` key (with the input to the tool going here).

The only values that should be in the "action" field are:
get_weather: Get the current weather in a given location, args: {"location": {"type": "string"}}
calculate_shipping_sla: Calculate the estimated time of arrival of a sla delivery based on a distance, args: {"distance_km": {"type": "integer"}}

example use :

{{
  "action": "get_weather",
  "action_input": {"location": "New York"}
}}


ALWAYS use the following format:

Question: the input question you must answer
Thought: you should always think about one action to take. Only one action at a time in this format:
Action:

$JSON_BLOB (inside markdown cell)

Observation: the result of the action. This Observation is unique, complete, and the source of truth.
(this Thought/Action/Observation can repeat N times, you should take several steps when needed. The $JSON_BLOB must be formatted as markdown and only use a SINGLE action at a time.)

You must always end your output with the following format:

Thought: I now know the final answer
Final Answer: the final answer to the original input question

Now begin! Reminder to ALWAYS use the exact characters `Final Answer:` when you provide a definitive answer. """

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "What is the weather in spain?"},
]

output = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=messages,
    stream=False,
    max_tokens=1024,
    extra_body={'thinking': {'type': 'disabled'}},
    stop=["Observation:"]
)

def parse_action_and_params(text:str) -> tuple[str,dict]:
    match = re.search(r"```json\s(\{.*?\})\s```", text, re.DOTALL)

    if match:
        json_str = match.group(1)
    else:
        start = text.find("{")
        end = text.find("}")
        json_str = text[start:end]

    data = json.loads(json_str)

    action = data["action"]
    params = data["action_input"]

    return action, params


# A action que a LLM identificou para executar estará aqui dentro, como a gnt especificou o formato em que ela tem que devolver a action a ser usada, isso facilita para fazer um parsing, extrair a action e chamar a respectiva tool com o respectivo parametros
if output.choices[0].message.content:
    output_str = output.choices[0].message.content

    action, params = parse_action_and_params(output_str)

    messages.append(
        {"role": "assistant", "content": output.choices[0].message.content + "Observation:\n" + AVAILABLE_TOOLS[action](**params)},
    )

output = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=messages,
    stream=False,
    max_tokens=1024,
    extra_body={'thinking': {'type': 'disabled'}},
    stop=["Observation:"]
)

print(output.choices[0].message.content)