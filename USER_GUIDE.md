# 📘 User Guide – Excel/CSV Data Transformer (CrewAI + Gemini)

## 1. Overview

This project automates the process of:

* Inspecting **Excel/CSV files** (detecting headers, columns, metadata, preview).
* Generating **Python scripts** via CrewAI agents powered by Google Gemini API.
* Validating those scripts to ensure correctness.
* Running transformations (merge, clean, enrich, compute fields, etc.) described in user prompts.

It’s built with:

* **CrewAI** for orchestrating LLM agents.
* **Google Gemini API** for natural-language-to-code generation.
* **Custom Inspector Tool** to analyze uploaded files.

---

## 2. Project Structure

```
project-root/
│
├── backend/
│   ├── main.py                # FastAPI entrypoint
│   ├── crewmain.py            # Crew runner (loads env, runs tasks)
│   ├── crew.py                # CrewAI crew definition (agents, tasks, LLM)
│   ├── custom_tool.py         # Excel/CSV inspector tool
│   └── agents.yaml / tasks.yaml  # Configs for CrewAI agents/tasks
│
├── frontend/                  # UI (optional, if you’re running frontend)
│
├── .env                       # API keys & env variables
└── requirements.txt
```

---

## 3. Setup

### Step 1: Clone & Install

```bash
git clone <repo-url>
cd project-root
python -m venv venv
venv\Scripts\activate on Windows    # or source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Environment Variables

Create `.env` in project root:

```bash
# LLM API key
GEMINI_API_KEY=AIzaSy...      # Google AI Studio key

# LLM Model
LLM_MODEL=gemini/gemini-2.5-pro

CREWAI_TELEMETRY=false
```

👉 Keys **must** come from [Google AI Studio](https://aistudio.google.com/app/apikey), not Cloud Console.

### Step 3: Run Backend and Frontend

From project root (for backend):

```bash
uvicorn backend.main:app --reload --port 8000
```

If `backend` import errors occur:

```bash
PYTHONPATH=. uvicorn backend.main:app --reload --port 8000
```

From project root (for frontend):

```bash
cd frontend
streamlit run app.py
```

---

## 4. How It Works

1. **User uploads files + gives a prompt** (via API or UI).
2. `excel_data_inspector_tool` inspects each file:

   * Dynamically detects header rows (for both Excel & CSV).
   * Extracts metadata (rows, columns, size, types, sample values).
   * Returns structured JSON.
3. **CrewAI Agents**:

   * `script_generator`: creates a Python script for transformations.
   * `validator`: reviews and validates script correctness.
4. Final script is saved as `final_script.py` (or returned in API response).
5. User runs the script locally on their dataset for transformations.

---

## 5. Inspector Tool (Excel/CSV)

* Supports `.xlsx`, `.xls`, `.csv`.
* Detects first meaningful header row (skips blank/junk rows).
* Produces:

  * File metadata (rows, columns, size, file_type).
  * Column info (name, dtype, sample values).
  * Data preview (first 5 rows as JSON).

Example output (simplified):

```json
{
  "files_inspected": 1,
  "success": true,
  "files": [
    {
      "original_path": "data/sample.csv",
      "status": "success",
      "metadata": {"rows": 100, "columns": 12, "file_size": 53200, "file_type": ".csv"},
      "columns": [
        {"name": "Date", "dtype": "object", "non_null_count": 100, "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"]},
        {"name": "Value", "dtype": "float64", "non_null_count": 98, "sample_values": [12.4, 15.2, 14.8]}
      ],
      "preview": [
        {"Date": "2024-01-01", "Value": 12.4},
        {"Date": "2024-01-02", "Value": 15.2}
      ]
    }
  ]
}
```

---

## 6. Workflow for Users

### Step 1: Upload Files

* Place `.xlsx` or `.csv` files in accessible paths or upload them in the designated drag-and-drop holder.
* Ensure `.env` is set with a valid Gemini API key.

### Step 2: Run Crew

Send prompt + file paths by typing data transformation instructions and clicking `Generate Script` or via backend (API or script) by running:

```python
from backend.crewmain import run

prompt = "Merge all files and clean invalid values as per requirements."
files = ["./data/file1.xlsx", "./data/file2.csv"]

script = run(prompt, files)
print(script)
```

### Step 3: Download and execute Generated Script

Save the returned code as `transform.py` or download it by copying the script or clicking `Download Script as .py` and run:

```bash
python transform.py
```

---

## 7. Troubleshooting

* **❌ API key not valid**

  * Ensure `.env` is in project root.
  * Key must be from **AI Studio**, not GCP Console.
  * Restart server after editing `.env`.

* **❌ ModuleNotFoundError: backend**

  * Run from project root.
  * Try: `PYTHONPATH=. uvicorn backend.main:app --reload`.

* **❌ Columns missing**

  * Inspector scans first 20 rows to find headers; increase `max_search` if your data starts deeper.

* **Encoding errors with CSV**

  * First try: utf-8-sig (handles BOM from Excel exports)
  * Then try: utf-8 (standard UTF-8)
  * Fallback: latin-1, cp1252, iso-8859-1

---

## 8. Extending the Project

* **Multiple Excel sheets**: Extend inspector to iterate `pd.ExcelFile(...).sheet_names`.
* **Additional file types**: Add new loaders in inspector (e.g., `.parquet`, `.json`).
* **Custom transformations**: Update `tasks.yaml` and agent prompts.

---

✅ With this, any user can set up the project, configure Gemini, inspect Excel/CSV files, generate scripts, and run transformations.
