  # Root app: CORS, Lifespan, and Router mounting
  # app/main.py ke andar
from fastapi import FastAPI
from app.routers.documents import router as documents_router
# Baki routers bhi yahan honge (compliance, health, etc.)

app = FastAPI(title="FinGraph Copilot")

# Ensure karein ki yeh line wahan maujood ho:
app.include_router(documents_router)