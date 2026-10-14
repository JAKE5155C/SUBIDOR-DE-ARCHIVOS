import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI(title="Subir PDF")

UPLOAD_DIR = BASE_DIR / "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Subir PDF",
            "uploaded_file": None,
            "message": None,
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)) -> HTMLResponse:
    if not file.filename or Path(file.filename.replace("\\", "/")).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Selecciona un archivo PDF.")

    content = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="El PDF no puede superar 10 MB.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="El archivo seleccionado no es un PDF válido.")

    UPLOAD_DIR.mkdir(exist_ok=True)
    stored_name = f"{uuid4().hex}.pdf"
    (UPLOAD_DIR / stored_name).write_bytes(content)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Subir PDF",
            "uploaded_file": Path(file.filename.replace("\\", "/")).name,
            "message": None,
        },
    )


@app.post("/delete-uploads", response_class=HTMLResponse)
async def delete_uploads(request: Request) -> HTMLResponse:
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Subir PDF",
            "uploaded_file": None,
            "message": "Se eliminaron los archivos subidos.",
        },
    )
