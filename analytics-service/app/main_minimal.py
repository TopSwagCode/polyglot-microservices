from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Analytics Service"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )