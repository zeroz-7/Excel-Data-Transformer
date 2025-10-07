import os
from dotenv import load_dotenv

# Load env vars (Gemini key, etc.) BEFORE importing crew modules
# Force load .env from project root
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path)

import warnings
import traceback
import re
from datetime import datetime
from .crew import CsvOrganiser

import logging

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

logger = logging.getLogger(__name__)

def _sanitize_output(result_obj):
    """
    Extract clean Python code from a CrewAI result.
    Removes markdown fences and extra text.
    """
    # Get raw string
    raw = getattr(result_obj, "raw", str(result_obj)).strip()

    # Remove triple backtick fences if present
    code = re.sub(r"^```(?:python)?", "", raw.strip(), flags=re.IGNORECASE)
    code = re.sub(r"```$", "", code.strip())

    return code.strip()

def run(prompt: str, file_paths: list):
    """
    Entry point for the crew. Called from FastAPI (main.py).
    """
    # Defensive checks
    if not isinstance(file_paths, list):
        raise ValueError("file_paths must be a list of filesystem paths.")

    # Validate that files actually exist before starting crew
    missing_files = []
    for f_path in file_paths:
        if not os.path.exists(f_path):
            missing_files.append(f_path)
    
    if missing_files:
        error_msg = f"Files not found before crew execution: {missing_files}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

    # DEBUG: Check API key before crew execution
    api_key = os.getenv("GEMINI_API_KEY")
    logger.info(f"🔑 API Key before crew: {'LOADED' if api_key else 'MISSING'}")

    inputs = {
        "prompt": prompt,
        "files": file_paths,
        "files_str": "\n".join(file_paths),
        "current_year": str(datetime.now().year),
    }

    logger.info("Launching CsvOrganiser crew with inputs:")
    logger.info("files (list): %s", inputs["files"])

    try:
        result = CsvOrganiser().crew().kickoff(inputs=inputs)
        script = _sanitize_output(result)
        
        # Check if the result is an error message
        if script.strip().upper().startswith('ERROR:'):
            logger.error(f"❌ Agent returned error: {script}")
            raise Exception(script)
            
        return script
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error running crew: {str(e)}\n\n{error_details}")
        raise Exception(f"An error occurred while running the crew: {str(e)}")