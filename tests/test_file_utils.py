import os
import yaml
import sys
import pytest
from pathlib import Path

sys.path.append("..")
import file_utils as fu
import mystery_settings as msmod
from file_utils import write_outputs


def test_collect_game_files(tmp_path, tmp_yaml):
    tmp_yaml("a.yaml", {})
    tmp_yaml("b.yaml", {})
    os.makedirs(tmp_path / "sub")
    tmp_yaml("sub/c.yaml", {})

    files = fu.collect_game_files(tmp_path)
    assert len(files) == 3


def test_collect_game_files_empty(tmp_path):
    with pytest.raises(FileNotFoundError):
        fu.collect_game_files(tmp_path)


def test_write_outputs_count(tmp_path):
    out = tmp_path / "output"
    ms = msmod.MysterySettings("count")
    ms["game"] = {"foo": 2}
    ms.games_data["foo"] = {
        "file_path": "",
        "name": "Test",
        "description": "desc",
        "requires": {"x": 1},
        "options": {"setting": True},
    }

    fu.write_outputs(ms, "count", output_dir=str(out))

    assert (out / "foo_1.yaml").exists()
    assert (out / "foo_2.yaml").exists()


def test_write_outputs_weights(tmp_path):
    out = tmp_path / "output"
    ms = msmod.MysterySettings("weights")
    ms["game"] = {"foo": 1}
    ms.games_data["foo"] = {
        "file_path": "",
        "name": "Test",
        "description": "desc",
        "requires": {},
        "options": {"a": 1},
    }

    fu.write_outputs(ms, "weights", output_dir=str(out))

    assert (out / "games.yaml").exists()

    data = list(yaml.safe_load_all(open(out / "games.yaml", "r", encoding="utf-8")))
    assert len(data) == 1
    assert data[0]["game"] == "foo"
