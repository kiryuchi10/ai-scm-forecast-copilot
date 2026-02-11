# apps/api 안에서 uvicorn app.main:app --reload 사용 시 이 파일이 로드됩니다.
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from apps.api.main import app

__all__ = ["app"]
