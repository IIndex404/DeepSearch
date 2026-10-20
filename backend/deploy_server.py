"""Serve the API and the compiled Vue application from one local origin."""
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from api.server import app

root = Path(__file__).resolve().parent
frontend = root.parent / "frontend" / "dist"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "deepagent-search"}


if not (frontend / "index.html").is_file():
    raise RuntimeError("Frontend is not built. Run npm.cmd run build in frontend.")

app.mount("/outputs", StaticFiles(directory=root / "output"), name="outputs")
app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
