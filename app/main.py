from fastapi import FastAPI

app = FastAPI(title="cdmad-reference-vdb")


@app.get("/")
async def root():
    return {"service": "cdmad-reference-vdb", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
