import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Ensure src is on sys.path for imports when running via pytest
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Set default Flask secret to avoid warnings in tests
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")
