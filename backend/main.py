import os
import tempfile
import logging
import traceback
import inspect

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

try:
    from backend.crewai_app.crewmain import run
except Exception as e:
    run = None
    logging.getLogger(__name__).warning(
        f"Could not import 'run' from backend.crewai_app.crewmain: {e}"
    )

# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------
# Console: INFO-level only (so terminal isn’t spammed)
# File: DEBUG-level (so you can check full trace later in logs/backend.log)
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "backend.log")

logging.basicConfig(
    level=logging.DEBUG,  # root logger
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),                # console
        logging.FileHandler(log_file, mode="a", encoding="utf-8")  # file
    ]
)

logging.getLogger("crewai").setLevel(logging.DEBUG)
logging.getLogger("backend.crewai_app").setLevel(logging.DEBUG)

# Silence noisy libs in console
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.INFO)

logger = logging.getLogger("backend.main")

# -----------------------------------------------------------------------------
# FastAPI app setup
# -----------------------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Endpoint
# -----------------------------------------------------------------------------
@app.post("/transform")
async def transform(prompt: str = Form(...), files: Optional[List[UploadFile]] = File(None)):
    if not files:
        return {"error": "No files uploaded."}

    if run is None:
        return {"status": "error", "error": "Server misconfiguration: crew runner 'run' not available."}

    saved_files = []
    try:
        logger.info(f"Processing {len(files)} Excel files with prompt: {prompt[:120]}")

        # Save files and verify they exist
        for file in files:
            filename = getattr(file, "filename", None) or "upload.xlsx"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            tmp.close()
            saved_files.append(tmp.name)
            logger.info(f"Saved temporary Excel file: {tmp.name} (original: {filename})")

        # Verify files exist before calling crew
        for path in saved_files:
            if not os.path.exists(path):
                raise Exception(f"Temporary file not created: {path}")

        logger.info("Starting crew execution...")
        result = run(prompt, saved_files)

        if inspect.isawaitable(result):
            result = await result

        logger.info("Crew execution completed successfully")
        return {"status": "success", "script": result}

    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        logger.error(traceback.format_exc())
        # Return detailed error for frontend display
        return {"status": "error", "error": str(e), "details": traceback.format_exc()}
    finally:
        for path in saved_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Removed temporary file: {path}")
            except Exception as e:
                logger.error(f"Error deleting temp file {path}: {e}")


@app.get("/test-api-key")
async def test_api_key():
    """Test endpoint to debug API key issues"""
    import os
    from dotenv import load_dotenv
    from litellm import completion
    
    # Test 1: Check if .env is loaded
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    result = {
        "env_loaded": True,
        "api_key_found": bool(api_key),
        "api_key_preview": api_key[:10] + "..." if api_key else "MISSING",
        "api_key_length": len(api_key) if api_key else 0,
        "test_result": None,
        "error": None
    }
    
    # Test 2: Try direct API call
    if api_key:
        try:
            response = completion(
                model="gemini/gemini-2.5-flash",
                api_key=api_key,
                messages=[{"role": "user", "content": "Say hello in one word"}],
                max_tokens=10
            )
            result["test_result"] = response.choices[0].message.content
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
    else:
        result["error"] = "No API key found"
        result["success"] = False
    
    return result

@app.get("/test-crew-llm")
async def test_crew_llm():
    """Test the crew's LLM configuration directly"""
    try:
        from backend.crewai_app.crew import CsvOrganiser
        
        # Create crew instance and get LLM config
        crew = CsvOrganiser()
        llm = crew._get_llm()
        
        result = {
            "llm_model": getattr(llm, 'model', 'Unknown'),
            "llm_api_key_set": bool(getattr(llm, 'api_key', None)),
            "llm_api_key_preview": getattr(llm, 'api_key', '')[:10] + "..." if getattr(llm, 'api_key', None) else "MISSING",
            "test_result": None,
            "error": None
        }
        
        # Test the LLM directly
        try:
            # This tests if the LLM object can make calls
            from litellm import completion
            test_response = completion(
                model=llm.model,
                api_key=llm.api_key,
                messages=[{"role": "user", "content": "Say 'test successful'"}],
                max_tokens=10
            )
            result["test_result"] = test_response.choices[0].message.content
            result["success"] = True
        except Exception as e:
            result["error"] = f"LLM call failed: {str(e)}"
            result["success"] = False
            
    except Exception as e:
        result = {
            "error": f"Failed to create crew LLM: {str(e)}",
            "success": False
        }
    
    return result