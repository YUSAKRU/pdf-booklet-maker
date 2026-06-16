#!/usr/bin/env python3
"""
Launcher script for pdf-booklet-maker Local Web UI.
"""
import uvicorn
from pdf_booklet.logger import get_logger

logger = get_logger()

def main():
    logger.info("Initializing Local Web UI", details={"host": "127.0.0.1", "port": 8000})
    print("==================================================================")
    print(" 📖 pdf-booklet-maker Local Web UI is starting!")
    print(" 👉 Open your browser and navigate to: http://127.0.0.1:8000")
    print(" 💡 Press Ctrl+C in this terminal to stop the server.")
    print("==================================================================")
    
    from pdf_booklet.web.server import app
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
