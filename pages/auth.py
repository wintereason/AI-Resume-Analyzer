import importlib.util
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
AUTH_PATH = ROOT_DIR / "auth.py"

if ROOT_DIR not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if AUTH_PATH.exists():
    spec = importlib.util.spec_from_file_location("root_auth", AUTH_PATH)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        for name in dir(module):
            if not name.startswith("_"):
                globals()[name] = getattr(module, name)
