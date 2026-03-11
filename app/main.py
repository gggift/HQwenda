from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="HQwenda", description="金融行情数据智能问答系统")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
