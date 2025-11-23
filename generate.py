import os
import sys

from config_loader import load_config
from mystery_settings import MysterySettings
from file_utils import collect_game_files, write_outputs


def _config_path_from_argv(default: str = "async.yaml") -> str:
    """
    Get the configuration file path from command-line arguments.

    Usage:
        python generate.py            -> uses default "async.yaml"
        python generate.py config.yml -> uses "config.yml"
    """
    return sys.argv[1] if len(sys.argv) > 1 else default


def main(config_path: str | None = None, output_dir: str = "output") -> None:
    # Load configuration
    if config_path is None:
        config_path = _config_path_from_argv()
    cfg, generation, *_ = load_config(config_path)

    mystery = MysterySettings(generation=generation)

    # Initialize RAW values from config
    for gname, val in cfg.get("game", {}).items():
        mystery["game"][gname] = int(val)

    # Add game metadata from YAML files
    game_files = collect_game_files()
    for path in game_files:
        filename_key = os.path.splitext(os.path.basename(path))[0]
        # Align YAML with config key if it exists
        key = filename_key if filename_key in mystery["game"] else None
        mystery.add_game(path, key=key)

    # Write outputs
    write_outputs(mystery, generation, output_dir=output_dir)

    print("\nEstimated game distribution:\n")
    print(mystery)


if __name__ == "__main__":
    main()
