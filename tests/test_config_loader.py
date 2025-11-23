import pytest
from pathlib import Path

# Import from cleaned module
import sys
sys.path.append("..")
import config_loader as cfgmod


def test_load_config_valid(tmp_yaml):
    cfg_file = tmp_yaml("config.yaml", {
        "generation": "count",
        "game": {"foo": 2}
    })
    cfg, generation, max_rank, rank_mult = cfgmod.load_config(cfg_file)

    assert generation == "count"
    assert cfg["game"]["foo"] == 2
    assert max_rank == 1
    assert rank_mult == 1.0


def test_load_config_missing_file():
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load_config("/no/such/file.yaml")


def test_load_config_invalid_generation(tmp_yaml):
    cfg_file = tmp_yaml("config.yaml", {"generation": "badvalue"})
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load_config(cfg_file)


def test_load_config_yaml_error(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(":\n:bad yaml!", encoding="utf-8")

    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load_config(bad)
