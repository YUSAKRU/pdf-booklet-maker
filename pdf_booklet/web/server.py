import os
import re
import sys
import uuid
import shutil
import zipfile
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from pdf_booklet.engine import BookletEngine
from pdf_booklet.exceptions import BookletError
from pdf_booklet.logger import get_logger

logger = get_logger()
app = FastAPI(title="pdf-booklet-maker API")

MAX_UPLOAD_BYTES = 200 * 1024 * 1024  # 200 MB
_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')

# Resolve paths dynamically (compatible with PyInstaller bundle structures)
IS_FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

if IS_FROZEN:
    # PyInstaller temporary directory (read-only bundle resources)
    STATIC_DIR = os.path.join(sys._MEIPASS, "pdf_booklet", "web", "static")
    # For session state, write to a local writable folder in the current working directory
    SESSIONS_DIR = os.path.join(os.getcwd(), ".pdf_booklet_sessions")
else:
    # Standard Python development directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    SESSIONS_DIR = os.path.join(BASE_DIR, ".sessions")

os.makedirs(SESSIONS_DIR, exist_ok=True)

@app.post("/api/process")
async def process_pdf(
    file: UploadFile = File(...),
    gutter: float = Form(0.0),
    creep: float = Form(0.0)
):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(SESSIONS_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a PDF."
        )

    # Enforce upload size limit
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {MAX_UPLOAD_BYTES // (1024*1024)} MB."
        )
    await file.seek(0)

    # Save uploaded file
    input_filename = "input.pdf"
    input_path = os.path.join(session_path, input_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error("Failed to save uploaded file", details={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file."
        )

    logger.info("Web upload received", details={
        "session_id": session_id,
        "filename": file.filename,
        "gutter": gutter,
        "creep": creep
    })

    try:
        # Run Booklet imposition
        engine = BookletEngine()
        result = engine.make_booklet(
            input_path=input_path,
            output_dir=session_path,
            base_gutter=gutter,
            creep_step=creep
        )

        # Create a ZIP containing both outputs
        base_name = os.path.basename(os.path.splitext(file.filename)[0]) or "output"
        zip_filename = f"{base_name}_booklet.zip"
        zip_path = os.path.join(session_path, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.write(result["front_pdf"], os.path.basename(result["front_pdf"]))
            zip_file.write(result["back_pdf"], os.path.basename(result["back_pdf"]))

        # Build response links
        response_data = {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "original_pages": result["original_pages"],
            "padded_pages": result["padded_pages"],
            "padding_applied": result["padding_applied"],
            "sheets_count": result["sheets_count"],
            "download_urls": {
                "front": f"/api/download/{session_id}/front",
                "back": f"/api/download/{session_id}/back",
                "zip": f"/api/download/{session_id}/zip"
            }
        }
        return JSONResponse(content=response_data)

    except BookletError as e:
        # Clean up session directory on error
        shutil.rmtree(session_path, ignore_errors=True)
        logger.error("Web processing error", details={"session_id": session_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        shutil.rmtree(session_path, ignore_errors=True)
        logger.error("Web unexpected processing error", exc_info=True, details={"session_id": session_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {str(e)}"
        )

@app.get("/api/download/{session_id}/{file_type}")
async def download_file(session_id: str, file_type: str, inline: bool = False):
    if not _UUID_RE.match(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID."
        )
    session_path = os.path.join(SESSIONS_DIR, session_id)
    if not os.path.exists(session_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired."
        )

    # Locate files in session directory
    files = os.listdir(session_path)
    front_file = next((f for f in files if f.endswith("_front.pdf")), None)
    back_file = next((f for f in files if f.endswith("_back.pdf")), None)
    zip_file = next((f for f in files if f.endswith("_booklet.zip")), None)

    if file_type == "front" and front_file:
        file_path = os.path.join(session_path, front_file)
        if inline:
            return FileResponse(file_path, media_type="application/pdf")
        return FileResponse(file_path, media_type="application/pdf", filename=front_file)
    elif file_type == "back" and back_file:
        file_path = os.path.join(session_path, back_file)
        if inline:
            return FileResponse(file_path, media_type="application/pdf")
        return FileResponse(file_path, media_type="application/pdf", filename=back_file)
    elif file_type == "zip" and zip_file:
        file_path = os.path.join(session_path, zip_file)
        return FileResponse(file_path, media_type="application/zip", filename=zip_file)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested file type not found."
        )

# Serve static web folder
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Web UI assets not found.")
