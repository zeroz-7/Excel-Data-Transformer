import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print("Loaded key:", key[:10] if key else "MISSING")

response = completion(
    model="gemini/gemini-2.5-flash",
    api_key=key,
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response)
