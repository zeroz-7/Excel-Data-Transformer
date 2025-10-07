import os
import pandas as pd
import json
from crewai.tools import tool
from typing import List, Dict, Any
import logging
import tempfile

import numpy as np

# Add this custom JSON encoder function at the top of the file, after imports
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)

logger = logging.getLogger(__name__)

@tool("Excel Data Inspector Tool")
def excel_data_inspector_tool(file_paths: List[str]) -> str:
    """
    Inspect each provided Excel file and return JSON structure.
    CRITICAL: If files are not found, return explicit error to halt the process.
    """
    results = {
        "files_inspected": 0,
        "files": [],
        "errors": [],
        "success": False  # Add overall success flag
    }

    if not file_paths or not isinstance(file_paths, list):
        return json.dumps({"error": "A list of file paths must be provided.", "success": False})

    logger.info(f"🔍 Inspecting {len(file_paths)} files: {file_paths}")

    for path in file_paths:
        original_path = path
        resolved_path = None
        file_result = {
            "original_path": original_path,
            "resolved_path": None,
            "status": "not_found",
            "metadata": {},
            "columns": [],
            "preview": []
        }

        # Check if path exists directly
        if os.path.exists(path):
            resolved_path = path
            logger.info(f"✅ File found at original path: {path}")
        else:
            # Try to find the file in various locations
            basename = os.path.basename(path)
            
            # Check in current working directory
            cwd_path = os.path.join(os.getcwd(), basename)
            if os.path.exists(cwd_path):
                resolved_path = cwd_path
                logger.info(f"✅ File found in CWD: {cwd_path}")
            
            # Check in temp directory
            if not resolved_path:
                tmp_dir = tempfile.gettempdir()
                tmp_path = os.path.join(tmp_dir, basename)
                if os.path.exists(tmp_path):
                    resolved_path = tmp_path
                    logger.info(f"✅ File found in temp dir: {tmp_path}")

        # CRITICAL: If file not found, return explicit error
        if not resolved_path:
            error_msg = f"❌ File not found: {original_path}. File does not exist at provided path or in temp directory."
            logger.error(error_msg)
            file_result["status"] = "not_found"
            file_result["error"] = error_msg
            results["errors"].append(error_msg)
            results["files"].append(file_result)
            continue  # Continue to check other files

        file_result["resolved_path"] = resolved_path

        try:
            logger.info(f"📖 Reading Excel file: {resolved_path}")
            df = pd.read_excel(resolved_path, engine="openpyxl", nrows=10)
            
            # File metadata
            file_result["status"] = "success"
            file_result["metadata"] = {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "file_size": os.path.getsize(resolved_path) if os.path.exists(resolved_path) else 0
            }
            
            # Column information
            file_result["columns"] = [
                {
                    "name": str(col),
                    "dtype": str(df[col].dtype),
                    "non_null_count": df[col].count(),
                    "sample_values": df[col].head(3).fillna('').tolist()
                }
                for col in df.columns
            ]
            
            # Preview data
            preview_data = df.head().where(pd.notna(df), None)
            file_result["preview"] = preview_data.fillna('').to_dict('records')
            
            results["files_inspected"] += 1
            logger.info(f"✅ Successfully inspected: {resolved_path}")

        except Exception as e:
            error_msg = f"❌ Error reading {resolved_path}: {str(e)}"
            logger.exception(error_msg)
            file_result["status"] = "error"
            file_result["error"] = error_msg
            results["errors"].append(error_msg)

        results["files"].append(file_result)

    # Set overall success based on whether any files were successfully inspected
    results["success"] = results["files_inspected"] > 0
    
    logger.info(f"📊 Inspection completed. Success: {results['success']}, Files inspected: {results['files_inspected']}")
    
    if not results["success"] and results["errors"]:
        logger.error("❌ NO files could be inspected. Halting process.")
    
    return json.dumps(results, indent=2, cls=NumpyEncoder)