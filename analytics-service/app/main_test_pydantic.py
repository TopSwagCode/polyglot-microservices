from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import datetime

app = FastAPI()

# Test simple Pydantic model
class SimpleModel(BaseModel):
    name: str
    age: int

@app.get("/")
async def root():
    return {"message": "Testing Pydantic"}

@app.post("/test")
async def test_model(data: SimpleModel):
    return {"received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)