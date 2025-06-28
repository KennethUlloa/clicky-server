import sys
import os
from app.main import run
from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".flaskenv")

kwargs = {
    "port": int(os.getenv("FLASK_PORT", 5000)),
    "host": os.getenv("FLASK_HOST", "0.0.0.0"),
    "debug": bool(int(os.getenv("FLASK_DEBUG", 0)))
}

for arg in sys.argv[1:]:
    parts = arg.split("=")
    if len(parts) == 2:
        key, value = parts
        key = key.removeprefix("--")
        kwargs[key] = value
        if key == "port":
            kwargs[key] = int(value)
    
    elif len(parts) == 1 and parts[0].startswith("--"):
        kwargs[parts[0].removeprefix("--")] = True

run(**kwargs)