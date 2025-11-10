import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow-API",
    description="Async Task Manager with JWT and Roles",
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
