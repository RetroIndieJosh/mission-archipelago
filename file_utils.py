import os
import yaml

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
      - games.yaml: full game options + metadata
      - weights.yaml: only options, metadata keys removed (weights mode only)
      - meta.yaml: placeholder meta info
    In count mode, generates multiple copies of each game in games.yaml according to the count.
    """
    os.makedirs("output", exist_ok=True)
    games_path = os.path.join("output", "games.yaml")
    weights_path = os.path.join("output", "weights.yaml")
    meta_path = os.path.join("output", "meta.yaml")

    # Write games.yaml
    with open(games_path, "w", encoding="utf-8") as gf:
        for i, game in enumerate(mystery["game"]):
            count = mystery["game"][game] if generation == "count" else 1
            for _ in range(count):
                options = mystery.games_data[game]["options"].copy()

                # Dump gameplay options under the game key
                yaml.dump({game: options}, gf, sort_keys=False)
                gf.write("\n")

                # Dump metadata
                metadata = {
                    "description": mystery.games_data[game]["description"],
                    "game": game,
                    "name": mystery.games_data[game]["name"],
                    "requires": mystery.games_data[game]["requires"],
                }
                yaml.dump(metadata, gf, sort_keys=False)
                gf.write("\n---\n\n")

    # Write weights.yaml (only in weights mode)
    if generation == "weights":
        with open(weights_path, "w", encoding="utf-8") as wf:
            for game, data in mystery.games_data.items():
                options = data["options"].copy()
                # Remove metadata keys
                for meta_key in ("name", "description", "requires", "game"):
                    options.pop(meta_key, None)
                yaml.dump({game: options}, wf, sort_keys=False)
                wf.write("\n")

    # Write a simple meta.yaml
    meta = {
        "meta_description": "Generated from Mission Archipelago",
        None: {"progression_balancing": 0},
    }
    with open(meta_path, "w", encoding="utf-8") as mf:
        yaml.dump(meta, mf, sort_keys=False)
