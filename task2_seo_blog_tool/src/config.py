from pathlib import Path
import os
from dotenv import load_dotenv

# Root of the workspace (two levels up from this file)
ROOT = Path(__file__).resolve().parents[2]
# Load .env in workspace root if present
load_dotenv(ROOT / '.env')

BLOGS_DIR = Path(os.getenv('BLOGS_DIR', str(Path(__file__).resolve().parents[1] / 'blogs')))
DEVTO_API_KEY = os.getenv('DEVTO_API_KEY', '')


def is_token_valid(token: str) -> bool:
    if not token:
        return False
    token = token.strip()
    if token.startswith('your_'):
        return False
    return True
