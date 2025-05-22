import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work whether this script is run
# from the project root or from within the api package directory
ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / 'api'
if API_ROOT.exists() and str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from fastapi.openapi.utils import get_openapi
from api.main import app
import json


def main():
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    json.dump(schema, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
