from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core import Settings
import gradio as gr
import requests
import os
from dotenv import load_dotenv

# Carica variabili ambiente
load_dotenv()

# Classe semplice per API HuggingFace
class HuggingFaceAPI:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model = "microsoft/Phi-3-mini-4k-instruct"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def complete(self, prompt):
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.1}
        }
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.model}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        else:
            return f"Errore API: {response.status_code}"

# Configura LLM tramite API HuggingFace invece che locale
llm = HuggingFaceAPI()

# 1. Caricamento documenti dalla cartella dedicata
documents = SimpleDirectoryReader("./docs").load_data()

# 2. Usa embeddings di default (leggeri) invece di Phi-3-mini locale
Settings.llm = llm

# 3. Costruzione dell'indice e query engine
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# 4. Funzione per rispondere alle domande (identica alla tua)
def ask_pdf(question):
    response = query_engine.query(question)
    return str(response)

# 5. Interfaccia Gradio (identica alla tua)
demo = gr.Interface(
    fn=ask_pdf,
    inputs=gr.Textbox(label="Fai una domanda sul PDF ABB"),
    outputs="text",
    title="Consulente Fotovoltaico (PDF ABB) - Phi-3 API"
)

if __name__ == "__main__":
    demo.launch()