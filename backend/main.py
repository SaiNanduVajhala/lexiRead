"""
FastAPI application - Dyslexia-Friendly Reading Companion API.
"""
import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from llm_service import GemmaService

app = FastAPI(
    title="Dyslexia Reading Companion API",
    description="Simplifies complex text for users with reading difficulties.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemma = GemmaService()

# Serve the frontend directory as static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "lexiRead")
if os.path.isdir(FRONTEND_DIR):
    print(f"[OK] Serving frontend from: {os.path.abspath(FRONTEND_DIR)}")


class TextRequest(BaseModel):
    text: str
    custom_prompt: str | None = None


class DeepDiveRequest(BaseModel):
    section_type: str
    section_content: str
    original_text: str

class DefineRequest(BaseModel):
    word: str
    context_sentence: str

@app.post("/define-word")
async def define_word(request: DefineRequest, x_api_key: str = Header(None)):
    if not request.word.strip() or not request.context_sentence.strip():
        raise HTTPException(status_code=400, detail="Word and context sentence cannot be empty.")
    
    result = await gemma.define_word(request.word.strip(), request.context_sentence.strip(), api_key=x_api_key)
    return result


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Dyslexia Reading Companion API is running."}


@app.post("/process-text")
async def process_text(request: TextRequest, x_api_key: str = Header(None)):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    if len(request.text) > 10000:
        raise HTTPException(status_code=400, detail="Text is too long. Please keep it under 10,000 characters.")

    result = await gemma.process_text(request.text.strip(), custom_prompt=request.custom_prompt, api_key=x_api_key)
    return result


@app.post("/deep-dive")
async def deep_dive(request: DeepDiveRequest, x_api_key: str = Header(None)):
    if not request.section_content or not request.section_content.strip():
        raise HTTPException(status_code=400, detail="Section content cannot be empty.")

    result = await gemma.deep_dive(
        section_type=request.section_type,
        section_content=request.section_content.strip(),
        original_text=request.original_text.strip(),
        api_key=x_api_key
    )
    return result


from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Index file not found")

# Mount static files LAST so API routes take priority
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="lexiread")

