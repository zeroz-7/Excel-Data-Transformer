import os
from dotenv import load_dotenv

# Load env vars (Gemini key, etc.) BEFORE importing crew modules
load_dotenv()

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
    - prompt: user input
    - file_paths: list of Excel file paths (saved in temp dir)
    """
    # Defensive checks
    if not isinstance(file_paths, list):
        raise ValueError("file_paths must be a list of filesystem paths.")

    # Provide both raw list and readable string for the agent. This ensures the agent sees absolute paths.
    inputs = {
        "prompt": prompt,
        "files": file_paths,                   # raw list used by tools
        "files_str": "\n".join(file_paths),    # human-friendly and LLM-friendly representation
        "current_year": str(datetime.now().year),
    }

    # Log exactly what we're passing in
    logger.info("Launching CsvOrganiser crew with inputs:")
    logger.info("prompt: %s", (prompt[:200] + "...") if len(prompt) > 200 else prompt)
    logger.info("files (list): %s", inputs["files"])
    logger.info("files_str (preview): %s", inputs["files_str"][:500].replace("\n", " | "))

    try:
        result = CsvOrganiser().crew().kickoff(inputs=inputs)

        # Always sanitize to return only Python code
        script = _sanitize_output(result)

        return script
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error running crew: {str(e)}\n\n{error_details}")
        raise Exception(f"An error occurred while running the crew: {str(e)}")
