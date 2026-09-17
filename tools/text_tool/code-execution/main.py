import os
from pathlib import Path
from secrets import compare_digest

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="Text Tool", version="1.0.0")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    configured_key = os.getenv("TOOL_API_KEY")
    if not configured_key or not api_key or not compare_digest(api_key, configured_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


@app.get("/")
def root() -> dict[str, str]:
    return {"tool": "text", "status": "ready"}


@app.post("/analyze")
def analyze(
    request: TextRequest,
    _: None = Depends(require_api_key),
) -> dict[str, int]:
    words = request.text.split()
    return {
        "characters": len(request.text),
        "words": len(words),
        "lines": len(request.text.splitlines()),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
    )
