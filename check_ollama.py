# check_ollama.py
import requests
import subprocess
import os

def check_ollama():
    try:
        # Check if port 11434 is available
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print("✅ Ollama is running and responding")
        return True
    except requests.ConnectionError:
        print("❌ Ollama is not running on port 11434")
        
        # Try to start Ollama
        try:
            print("🚀 Attempting to start Ollama...")
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("✅ Ollama started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False

if __name__ == "__main__":
    check_ollama()