
import gradio as gr
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.llms import HuggingFaceHub
from tools.calculate_pv_output import calculate_pv_output

# LLM economico (es. HuggingFaceHub, oppure sostituisci con OpenAI se necessario)
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.1",  # sostituibile con un modello locale/HF
    model_kwargs={"temperature": 0.1, "max_new_tokens": 512}
)

# Tool: calcolo PV
tools = [
    Tool(
        name="CalcoloProduzioneFotovoltaica",
        func=calculate_pv_output,
        description="Usa questo tool per stimare la produzione energetica da un impianto fotovoltaico. Richiede: latitudine, longitudine, efficienza, azimut, inclinazione, potenza modulo, perdite e anno."
    )
]

# Agente
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Interfaccia Gradio
demo = gr.Interface(
    fn=lambda message: agent.run(message),
    inputs=gr.Textbox(label="Scrivi la tua richiesta (es. calcola la produzione a Roma, inclinazione 30°, azimut 0°)"),
    outputs="text",
    title="Agente Calcolo Produzione Fotovoltaica"
)

if __name__ == "__main__":
    demo.launch()