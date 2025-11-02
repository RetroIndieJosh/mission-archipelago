import os
import yaml
import shutil
import copy

def collect_game_files(settings_dir="settings"):
    """
    Collect all YAML files recursively under `settings_dir`.
    Returns a list of file paths.
    """
    files = []
    for root, _, fns in os.walk(settings_dir):
        for fn in fns:
            if fn.endswith(".yaml"):
                files.append(os.path.join(root, fn))
    if not files:
        raise FileNotFoundError(f"No YAML files found under `{settings_dir}/`.")
    return files


def write_outputs(mystery, generation: str):
    """
    Writes output files:
      - Count mode: one YAML file per game instance
      - Weights mode: combined games.yaml
    Metadata and game key are at the top level.
    Clears the 'output' directory before writing.
    """
    output_dir = "output"

    # Clear output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    if generation == "count":
        # One YAML per game instance
        for game, count in mystery["game"].items():
            for i in range(1, count + 1):
                output_file = os.path.join(output_dir, f"{game}_{i}.yaml")
                with open(output_file, "w", encoding="utf-8") as gf:
                    # Deep copy to avoid YAML anchors
                    options_copy = copy.deepcopy(mystery.games_data[game]["options"])

                    # If options already has the game as top-level key, extract inner dict
                    if game in options_copy:
                        options_copy = options_copy[game]

                    # Remove any leftover metadata keys
                    for meta_key in ("name", "description", "requires"):
                        options_copy.pop(meta_key, None)

                    requires_copy = copy.deepcopy(mystery.games_data[game]["requires"])

                    # Build final dict
                    data = {
                        "game": game,
                        "name": mystery.games_data[game]["name"],
                        "description": mystery.games_data[game]["description"],
                        "requires": requires_copy,
                        game: options_copy
                    }

                    yaml.safe_dump(data, gf, sort_keys=False)
                print(f"Wrote {output_file}")

    else:
        # Weights mode: single combined games.yaml
        games_path = os.path.join(output_dir, "games.yaml")
        with open(games_path, "w", encoding="utf-8") as gf:
            for game, data_info in mystery.games_data.items():
                options_copy = copy.deepcopy(data_info["options"])

                if game in options_copy:
                    options_copy = options_copy[game]

                for meta_key in ("name", "description", "requires"):
                    options_copy.pop(meta_key, None)

                requires_copy = copy.deepcopy(data_info["requires"])

                data = {
                    "game": game,
                    "name": data_info["name"],
                    "description": data_info["description"],
                    "requires": requires_copy,
                    game: options_copy
                }

                yaml.safe_dump(data, gf, sort_keys=False)
                gf.write("\n")
        print(f"Wrote {games_path}")
