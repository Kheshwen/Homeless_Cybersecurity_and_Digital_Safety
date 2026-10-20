import os
import tempfile

# Use a throwaway database and no API key for tests
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["OPENAI_API_KEY"] = ""

from app.db.seed import run_seed  # noqa: E402

run_seed()
