from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TestModel(BaseModel):
    name: str
    age: int

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test")
def test_model():
    return TestModel(name="test", age=25)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)