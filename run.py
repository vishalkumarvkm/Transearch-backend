import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting TRANSEARCH Python Backend on http://{host}:{port}")
    print(f"API Docs available at http://localhost:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=True)
