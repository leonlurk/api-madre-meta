from fastapi import FastAPI
from app.routes import auth, messages, tokens

app = FastAPI(title="API Madre - CRM")


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(tokens.router, prefix="/tokens", tags=["Tokens"])

@app.get("/")
def home():
    return {"message": "API Madre funcionando correctamente"}