import os
import pandas as pd
from crewai.tools import tool
from typing import List
import logging

logger = logging.getLogger(__name__)

@tool("Excel Data Inspector Tool")
def excel_data_inspector_tool(file_paths: List[str]) -> str:
    """
    Reads a sample from the first provided Excel file to provide structure + preview.
    Returns a markdown-like string or an error message.
    """
    try:
        if not file_paths or not isinstance(file_paths, list):
            return "Error: A list of file paths must be provided."

        first_file_path = file_paths[0]
        if not os.path.exists(first_file_path):
            return f"Error: File not found at path: {first_file_path}"

        try:
            df = pd.read_excel(first_file_path, engine="openpyxl", skiprows=3)
        except Exception as e:
            logger.warning(f"Excel read with skiprows failed: {e}. Trying without skiprows.")
            df = pd.read_excel(first_file_path, engine="openpyxl")

        columns = df.columns.tolist()
        try:
            data_sample = df.head().to_markdown(index=False)
        except Exception:
            data_sample = df.head().to_string(index=False)

        return (
            f"### Excel File Structure and Sample\n\n"
            f"**File Path:** `{first_file_path}`\n\n"
            f"**Detected Columns ({len(columns)}):**\n{', '.join(columns)}\n\n"
            f"**Data Preview (first 5 rows):**\n{data_sample}"
        )

    except Exception as e:
        logger.exception("An error occurred while inspecting the Excel file")
        return f"An error occurred while inspecting the file: {str(e)}"
