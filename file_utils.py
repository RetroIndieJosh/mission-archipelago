import os
import shutil
from typing import Iterable

import yaml


def collect_game_files(settings_dir: str = "settings") -> list[str]:
    """
    Collect all YAML files recursively under `settings_dir`.

    Returns:
        A list of absolute or relative file paths.
    Raises:
        FileNotFoundError if no YAML files are found.
    """
    files: list[str] = []
    for root, _, fns in os.walk(settings_dir):
        for fn in fns:
            if fn.endswith(".yaml"):
                files.append(os.path.join(root, fn))

    if not files:
        raise FileNotFoundError(f"No YAML files found under `{settings_dir}/`.")

    return files


def _prepare_output_dir(output_dir: str = "output") -> str:
    """Clear and recreate the output directory."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def write_outputs(mystery, generation: str, output_dir: str = "output") -> None:
    """
    Writes output files based on the generation mode.

    Count mode:
        - One YAML file per game instance: output/{game}_{i}.yaml
    Weights mode:
        - Single combined games.yaml file with all games.
    """
    output_dir = _prepare_output_dir(output_dir)

    if generation == "count":
        _write_count_mode_outputs(mystery, output_dir)
    else:
        _write_weights_mode_outputs(mystery, output_dir)


def _iter_nonzero_games(mystery) -> Iterable[tuple[str, int]]:
    """Yield (game_name, count_or_weight) for non-zero entries."""
    for game, value in mystery["game"].items():
        if value:
            yield game, int(value)


def _write_count_mode_outputs(mystery, output_dir: str) -> None:
    """Write one YAML file per game instance in count mode."""
    for game, count in _iter_nonzero_games(mystery):
        for i in range(1, count + 1):
            output_file = os.path.join(output_dir, f"{game}_{i}.yaml")
            data = mystery.build_game_export(game)
            with open(output_file, "w", encoding="utf-8") as gf:
                yaml.safe_dump(data, gf, sort_keys=False)
            print(f"Wrote {output_file}")


def _write_weights_mode_outputs(mystery, output_dir: str) -> None:
    """Write a single games.yaml file containing all weighted games."""
    games_path = os.path.join(output_dir, "games.yaml")
    with open(games_path, "w", encoding="utf-8") as gf:
        first = True
        for game in sorted(mystery.games_data.keys()):
            if not first:
                gf.write("\n")
            first = False
            data = mystery.build_game_export(game)
            yaml.safe_dump(data, gf, sort_keys=False)
    print(f"Wrote {games_path}")
