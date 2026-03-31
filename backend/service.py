from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import spacy

from backend.src.postcard_syntax_analyzer.syntax_analyzer import TextSyntaxAnalyzer
from backend.src.postcard_syntax_analyzer.formatters import simplify_stats
from backend.src.postcard_syntax_analyzer.stat_aliases import to_russian_names

# Project root (two levels up from this file)
BASE_PATH = Path(__file__).parent.parent

# Load spaCy model once at startup
nlp = spacy.load("ru_core_news_lg")

app = FastAPI(title="Syntax Analysis API", description="Analyze syntactic complexity of texts")

# Serve static files from the frontend directory
app.mount("/static", StaticFiles(directory=BASE_PATH / "frontend"), name="static")

# Template configuration
templates = Jinja2Templates(directory=BASE_PATH / "frontend")


class AnalyzeRequest(BaseModel):
    text: str
    mode: str = "simple"  # "simple" or "full"


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main page with the interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze(request_data: AnalyzeRequest):
    """Main analysis endpoint."""
    if not request_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        analyzer = TextSyntaxAnalyzer(request_data.text, nlp)

        if request_data.mode == "simple":
            # Simplified response (averages and totals)
            result = simplify_stats(analyzer)
        else:
            # Full response (44 parameters), keys translated to Russian
            full_stats = analyzer.get_all_stats()
            result = to_russian_names(full_stats)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "model": "ru_core_news_lg"}


def main():
    import uvicorn
    uvicorn.run("backend.service:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
