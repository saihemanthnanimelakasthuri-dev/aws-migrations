import os
import logging
from pathlib import Path
from secrets import compare_digest

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)
app = FastAPI(title="Calculator Tool", version="1.0.0")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    configured_key = os.getenv("TOOL_API_KEY")
    if not configured_key or not api_key or not compare_digest(api_key, configured_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class CalculationRequest(BaseModel):
    first: float
    second: float
    operation: str = Field(pattern="^(add|subtract|multiply|divide)$")


@app.get("/")
def root() -> dict[str, str]:
    return {"tool": "calculator", "status": "ready"}


@app.post("/calculate")
def calculate(
    request: CalculationRequest,
    _: None = Depends(require_api_key),
) -> dict[str, float | str]:
    logger.info("Calculation requested: operation=%s", request.operation)
    logger.info("aaded one more print")
    if request.operation == "add":
        result = request.first + request.second
    elif request.operation == "subtract":
        result = request.first - request.second
    elif request.operation == "multiply":
        result = request.first * request.second
    else:
        if request.second == 0:
            return {"error": "Cannot divide by zero"}
        result = request.first / request.second

    return {
        "operation": request.operation,
        "result": result,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
    )
