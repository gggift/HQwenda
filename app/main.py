from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.chat import router

app = FastAPI(title="HQwenda", description="金融行情数据智能问答系统")
app.include_router(router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Static files (mount last so API routes take priority)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
