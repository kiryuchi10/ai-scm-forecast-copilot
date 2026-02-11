"""
API 서버 실행. 프로젝트 루트 또는 apps/api 에서 실행 가능.
  python apps/api/run.py
  또는 (apps/api 안에서) python run.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가 (apps.api 임포트용)
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

if __name__ == "__main__":
    import uvicorn
    from apps.api.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
