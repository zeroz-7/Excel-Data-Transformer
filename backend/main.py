import os
import tempfile
import logging
import traceback
import inspect

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List

try:
    from crewai_app.crewmain import run
except Exception as e:
    run = None
    logging.getLogger(__name__).warning(
        f"Could not import 'run' from backend.crewai_app.crewmain: {e}"
    )

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transform")
async def transform(prompt: str = Form(...), files: List[UploadFile] = File(...)):
    if run is None:
        return {"status": "error", "error": "Server misconfiguration: crew runner 'run' not available."}

    saved_files = []
    try:
        logger.info(f"Processing {len(files)} Excel files with prompt: {prompt[:120]}")

        for file in files:
            filename = getattr(file, "filename", None) or "upload.xlsx"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            tmp.close()
            saved_files.append(tmp.name)
            logger.info(f"Saved temporary Excel file: {tmp.name} (original: {filename})")

        logger.info("Starting crew execution...")
        result = run(prompt, saved_files)

        if inspect.isawaitable(result):
            result = await result

        logger.info("Crew execution completed successfully")
        return {"status": "success", "script": result}

    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "error": str(e)}
    finally:
        for path in saved_files:
            try:
                os.remove(path)
                logger.info(f"Removed temporary file: {path}")
            except Exception as e:
                logger.error(f"Error deleting temp file {path}: {e}")
