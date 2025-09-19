import os
import pandas as pd
from crewai.tools import tool
from typing import List
import logging
import tempfile

logger = logging.getLogger(__name__)

@tool("Excel Data Inspector Tool")
def excel_data_inspector_tool(file_paths: List[str]) -> str:
    """
    Inspect each provided Excel file (lightweight):
    - Report all column names
    - Show first 5 rows as preview
    
    Returns a markdown-like report for all files.
    """
    results = []

    if not file_paths or not isinstance(file_paths, list):
        return "Error: A list of file paths must be provided."

    for path in file_paths:
        original_path = path

        if not os.path.exists(path):
            # Try resolving basename in temp dir and cwd
            basename = os.path.basename(path)
            tmp_dir = tempfile.gettempdir()
            candidates = [
                os.path.join(os.getcwd(), basename),
                os.path.join(tmp_dir, basename),
            ]
            for fname in os.listdir(tmp_dir):
                if basename in fname:
                    candidates.append(os.path.join(tmp_dir, fname))
            found = next((c for c in candidates if os.path.exists(c)), None)
            if found:
                logger.info("Resolved missing path '%s' -> '%s'", path, found)
                path = found
            else:
                results.append(f"❌ File not found: {original_path}")
                continue

        try:
            df = pd.read_excel(path, engine="openpyxl")

            columns = df.columns.tolist()
            try:
                preview = df.head().to_markdown(index=False)
            except Exception:
                preview = df.head().to_string(index=False)

            results.append(
                f"### Excel File Summary\n"
                f"**File Path:** `{path}`\n\n"
                f"**Columns ({len(columns)}):** {', '.join(columns)}\n\n"
                f"**Preview (first 5 rows):**\n{preview}\n"
            )

        except Exception as e:
            logger.exception(f"Error inspecting {path}")
            results.append(f"⚠️ Error reading {path}: {e}")

    return "\n---\n".join(results) if results else "No valid Excel files inspected."
