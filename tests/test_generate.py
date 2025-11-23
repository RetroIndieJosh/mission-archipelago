import sys
import yaml
from pathlib import Path

sys.path.append("..")

import generate as gen


def test_generate_integration(tmp_path, tmp_yaml, monkeypatch):
    # Create config
    cfg_path = tmp_yaml("config.yaml", {
        "generation": "count",
        "game": {"x": 2}
    })

    # Create settings directory and game file
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    game_file = tmp_path / "settings/x.yaml"
    game_file.write_text(yaml.safe_dump({
        "name": "Game X",
        "description": "demo",
        "requires": {},
        "settingA": 1
    }))

    # Monkeypatch collect_game_files to use tmp settings
    import file_utils as fu
    monkeypatch.setattr(fu, "collect_game_files",
                        lambda _=None: [str(game_file)])

    # Monkeypatch output target directory
    monkeypatch.chdir(tmp_path)

    gen.main(str(cfg_path), output_dir=str(tmp_path / "output"))

    assert (tmp_path / "output/x_1.yaml").exists()
    assert (tmp_path / "output/x_2.yaml").exists()
