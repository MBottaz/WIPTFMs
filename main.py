from langchain.agents import initialize_agent, AgentType
from langchain_huggingface import HuggingFaceEndpoint
from tools.tool_def import estimate_pv_output_tool
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente da .env
load_dotenv()

# Leggi il token HF
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Setup del LLM da Hugging Face
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    temperature=0.1,
    max_new_tokens=512,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
)

# Inizializzazione dell'agente con il Tool
agent = initialize_agent(
    tools=[estimate_pv_output_tool],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Esecuzione
if __name__ == "__main__":
    response = agent.run(
        "Calculate the production for a PV plant, with coordinates latitude = 41.9, longitude = 12.5, using panels with a 30-degree tilt and azimuth 0, and an efficiency of 0.18."
    )
    print(response)