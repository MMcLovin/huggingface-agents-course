from smolagents import CodeAgent, LiteLLMModel, tool
import random

model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:7b",  
    api_base="http://127.0.0.1:11434",  
    num_ctx=8192,
)

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location.
    Args:
        location: The city or country to check the weather for.
    """
    temperature = random.randint(-5, 35)
    return f"The weather in {location} is {temperature}°C"

@tool
def calculate_shipping_sla(distance_km:int) -> str:
    """Calculate the expected delivery time for a package based on distance.
    Args:
        distance_km: The shipping distance in kilometers.
    """
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

agent = CodeAgent(
    tools=[get_weather, calculate_shipping_sla],
    model=model
)

agent.run("What is the weather in Spain, and how long will a delivery take for 12 km?")
