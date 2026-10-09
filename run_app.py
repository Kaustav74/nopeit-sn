"""
JEE Advanced AIR-1 & CBSE 95%+ Platform Launcher
Starts the FastAPI server with Uvicorn on http://127.0.0.1:8000
"""

import sys
import os

# Set UTF-8 encoding for stdout on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import init_db
import uvicorn

def main():
    print("=" * 60)
    print(" [AIR-1] INITIALIZING JEE ADVANCED AIR-1 & CBSE 95%+ COMPANION")
    print("=" * 60)
    print(" [*] Initializing SQLite Database...")
    init_db()
    print(" [*] Models & Curated Knowledge Vault Ready.")
    print(" [*] FreeLLM Endpoint Connected.")
    print(" [*] Server starting at: http://localhost:8000")
    print("=" * 60)

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
