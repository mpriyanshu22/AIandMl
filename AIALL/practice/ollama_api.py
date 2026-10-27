from fastapi import FastAPI
from ollama import Client
from fastapi import Body
app = FastAPI()
client=Client(
    host="http://localhost:11434"
)

client.pull('smollm2:135m')

@app.post("/chat")
def chat(message: str = Body(..., description="Chat Message")):
    response = client.chat(model="smollm2:135m",messages=[
       {"role":"user", "content":message}
    ])
    return response['message']['content']