import os
import shutil
from typing import Iterable

import yaml


def collect_game_files(settings_dir: str = "settings") -> list[str]:
    files: list[str] = []
    for root, _, fns in os.walk(settings_dir):
        for fn in fns:
            if fn.endswith(".yaml"):
                files.append(os.path.join(root, fn))

    if not files:
        raise FileNotFoundError(f"No YAML files found under `{settings_dir}/`.")

    return files


def _prepare_output_dir(output_dir: str = "output") -> str:
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def write_outputs(mystery, output_dir: str = "output") -> None:
    """
    Writes one YAML file per game instance.
    """
    output_dir = _prepare_output_dir(output_dir)
    _write_outputs(mystery, output_dir)


def _iter_nonzero_games(mystery) -> Iterable[tuple[str, int]]:
    for game, value in mystery["game"].items():
        if value > 0:
            yield game, value


def _write_outputs(mystery, output_dir: str) -> None:
    for game, count in _iter_nonzero_games(mystery):
        for i in range(1, count + 1):
            output_file = os.path.join(output_dir, f"{game}_{i}.yaml")
            data = mystery.build_game_export(game)
            with open(output_file, "w", encoding="utf-8") as gf:
                yaml.safe_dump(data, gf, sort_keys=False)
            print(f"Wrote {output_file}")
