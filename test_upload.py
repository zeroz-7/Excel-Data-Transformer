import requests
import os

API_URL = "http://127.0.0.1:8000/transform"

prompt = "Clean and merge all Excel files by 'ID'"

# 🔧 Replace these with real test Excel file paths on your system
file_paths = [
    r"C:\Users\Anush\Downloads\t1.xlsx",
    r"C:\Users\Anush\Downloads\t2.xlsx"
]

files = []
for path in file_paths:
    if not os.path.exists(path):
        print(f"❌ File not found locally: {path}")
        continue
    files.append((
        "files", 
        (os.path.basename(path), open(path, "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    ))

if not files:
    print("❌ No valid files to upload. Please check file paths.")
    exit(1)

print(f"➡️ Sending {len(files)} files to backend...")

try:
    resp = requests.post(API_URL, data={"prompt": prompt}, files=files, timeout=120)
    print("✅ Response status:", resp.status_code)
    print("🔎 Response body:")
    print(resp.text)
except Exception as e:
    print("❌ Error during request:", str(e))
