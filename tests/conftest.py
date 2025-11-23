import pytest
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def tmp_yaml(tmp_path):
    """
    Helper to create YAML files quickly.
    Returns a function (name, dict) -> file_path
    """
    def _create(name, content):
        path = tmp_path / name
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(content, f, sort_keys=False)
        return path
    return _create
