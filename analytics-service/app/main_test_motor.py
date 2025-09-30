from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import datetime

# Test importing motor which might be causing the issue
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    motor_imported = True
    motor_error = None
except Exception as e:
    motor_imported = False
    motor_error = str(e)

app = FastAPI()

class SimpleModel(BaseModel):
    name: str
    age: int

@app.get("/")
async def root():
    return {
        "message": "Testing Motor import",
        "motor_imported": motor_imported,
        "motor_error": motor_error
    }

@app.post("/test")
async def test_model(data: SimpleModel):
    return {"received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)