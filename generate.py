import os
import sys
import argparse
import yaml
from colorama import Fore


class MysterySettings(dict):
    """Hold configured weights/counts and per-game loaded data."""
    def __init__(self, generation: str):
        super().__init__()
        self["game"] = {}  # mapping game_name -> weight/count
        self.generation = generation
        self.games_data = {}  # mapping game_name -> {"options":..., "name":..., "description":..., "requires":...}

    def __str__(self) -> str:
        header_label = "#" if self.generation == "count" else "WGT"
        header = "{:<32} {:<6} {:>8}\n".format("GAME", header_label, "%")
        lines = ["-" * 52]
        for game, pct in sorted(self.weight_percentages().items(), key=lambda x: x[1], reverse=True):
            val = self["game"].get(game, 0)
            lines.append("{:<32} {:<6} {:>8}".format(game, val, "{:.1f}%".format(pct * 100)))
        return header + "\n".join(lines)

    def add_game(self, game_path: str):
        """Load game YAML. Flatten any nested key that matches the game name. Merge optional meta."""
        if not game_path.endswith(".yaml"):
            return

        print(f"Loading {game_path}...")
        try:
            with open(game_path, encoding="utf-8-sig") as f:
                payload = yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(Fore.RED + f"Missing file `{game_path}`" + Fore.WHITE)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(Fore.RED + f"YAML parse error in `{game_path}`: {e}" + Fore.WHITE)
            sys.exit(2)

        if not isinstance(payload, dict):
            print(Fore.RED + f"Game file `{game_path}` must be a mapping/dictionary." + Fore.WHITE)
            sys.exit(2)

        game = os.path.splitext(os.path.basename(game_path))[0]
        options = payload.copy()

        # Flatten nested key if top-level key matches the game name
        if game in options and isinstance(options[game], dict):
            options = options[game]

        # get metadata from original payload
        game_name_value = payload.get("name")
        if game_name_value is None:
            game_name_value = "Player-{player}"
            print(Fore.YELLOW + f"Warning: 'name' key missing for game `{game}`, using fallback '{game_name_value}'" + Fore.WHITE)

        game_description = payload.get("description", "")
        game_requires = payload.get("requires", {})

        # store options and metadata keys
        self.games_data[game] = {
            "options": options.copy(),
            "name": game_name_value,
            "description": game_description,
            "requires": game_requires,
        }

        # merge meta file if present
        meta_path = os.path.join("games", f"{game}.meta.yaml")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, encoding="utf-8-sig") as mf:
                    meta_payload = yaml.safe_load(mf) or {}
            except yaml.YAMLError as e:
                print(Fore.RED + f"YAML parse error in `{meta_path}`: {e}" + Fore.WHITE)
                sys.exit(2)

            if isinstance(meta_payload, dict):
                meta_options = meta_payload.get(game, meta_payload)
                if isinstance(meta_options, dict):
                    self.games_data[game]["options"].update(meta_options)


    def total_game_weights(self) -> int:
        return sum(int(v) for v in self["game"].values())

    def weight_percentages(self) -> dict:
        total = self.total_game_weights() or 1
        return {g: int(w) / total for g, w in self["game"].items()}


def parse_args():
    p = argparse.ArgumentParser(description="Mystery game YAML generator")
    p.add_argument("--file", type=str, default="async.yaml", help="Path to config YAML")
    return p.parse_args()


def validate_config(cfg: dict):
    required = ["generation", "categorize", "game"]
    for key in required:
        if key not in cfg:
            print(Fore.RED + f"Missing required key `{key}` in config." + Fore.WHITE)
            sys.exit(3)

    gen = cfg["generation"]
    if gen not in ("weights", "count"):
        print(Fore.RED + "generation must be 'weights' or 'count'." + Fore.WHITE)
        sys.exit(3)

    cat = cfg["categorize"]
    if cat not in ("rank", "all"):
        print(Fore.RED + "categorize must be 'rank' or 'all'." + Fore.WHITE)
        sys.exit(3)

    max_rank = cfg.get("max-rank")
    if cat == "rank" and (not isinstance(max_rank, int) or max_rank < 1):
        print(Fore.RED + "Missing or invalid `max-rank` for rank categorization." + Fore.WHITE)
        sys.exit(3)

    if not isinstance(cfg["game"], dict):
        print(Fore.RED + "`game` top-level key must be a mapping of game->weight/count." + Fore.WHITE)
        sys.exit(3)

    return gen, cat, max_rank


def collect_game_files(categorize: str, max_rank: int):
    files = []
    if categorize == "rank":
        for r in range(1, max_rank + 1):
            rank_dir = os.path.join("settings", f"Rank {r}")
            if not os.path.isdir(rank_dir):
                print(Fore.RED + f"Expected directory `{rank_dir}` missing." + Fore.WHITE)
                sys.exit(4)
            for fn in os.listdir(rank_dir):
                if fn.endswith(".yaml"):
                    files.append(os.path.join(rank_dir, fn))
    else:  # all
        for root, _, fns in os.walk("settings"):
            for fn in fns:
                if fn.endswith(".yaml"):
                    files.append(os.path.join(root, fn))
    if not files:
        print(Fore.RED + "No YAML files found under `settings/`." + Fore.WHITE)
        sys.exit(4)
    return files


def main():
    args = parse_args()
    try:
        with open(args.file, encoding="utf-8-sig") as cf:
            cfg = yaml.safe_load(cf) or {}
    except FileNotFoundError:
        print(Fore.RED + f"Config `{args.file}` not found." + Fore.WHITE)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(Fore.RED + f"YAML parse error in config `{args.file}`: {e}" + Fore.WHITE)
        sys.exit(2)

    generation_mode, categorize, max_rank = validate_config(cfg)

    # build mystery with only non-zero weights/counts
    mystery = MysterySettings(generation_mode)
    for gname, val in cfg["game"].items():
        try:
            w = int(val)
        except Exception:
            print(Fore.RED + f"Invalid weight/count for `{gname}`; must be integer-like." + Fore.WHITE)
            sys.exit(3)
        if w > 0:
            mystery["game"][str(gname)] = w

    # collect and load game files
    game_files = collect_game_files(categorize, max_rank)
    print(f"Found {len(game_files)} game files.")
    for path in game_files:
        mystery.add_game(path)

    # discard configured games not present in loaded files
    mystery["game"] = {g: v for g, v in mystery["game"].items() if g in mystery.games_data}

    # prepare outputs
    os.makedirs("output", exist_ok=True)
    weights_path = os.path.join("output", "weights.yaml")
    games_path = os.path.join("output", "games.yaml")
    meta_path = os.path.join("output", "meta.yaml")

    # write weights.yaml
    with open(weights_path, "w", encoding="utf-8") as wf:
        yaml.dump(dict(mystery), wf, sort_keys=False)

    # write games.yaml
    with open(games_path, "w", encoding="utf-8") as gf:
        games = list(mystery["game"].keys())
        for i, game in enumerate(games):
            options = mystery.games_data[game]["options"].copy()

            # remove metadata keys only for final gameplay options
            for meta_key in ("name", "description", "requires", "game"):
                options.pop(meta_key, None)

            # dump gameplay options under the game key
            yaml.dump({game: options}, gf, sort_keys=False)
            gf.write("\n")

            # dump metadata at top level
            metadata = {
                "description": mystery.games_data[game]["description"],
                "game": game,
                "name": mystery.games_data[game]["name"],
                "requires": mystery.games_data[game]["requires"],
            }
            yaml.dump(metadata, gf, sort_keys=False)

            if i < len(games) - 1:
                gf.write("\n---\n\n")

    # write meta.yaml
    meta = {
        "meta_description": "Generated from Mission Archipelago",
        None: {"progression_balancing": 0},
    }
    with open(meta_path, "w", encoding="utf-8") as mf:
        yaml.dump(meta, mf, sort_keys=False)

    # summary
    print()
    print(f"Mode: generation={generation_mode}, categorize={categorize}")
    print(f"Estimated game distribution:\n\n{mystery}")
    print(Fore.GREEN + "\nOutput written to ./output/ directory" + Fore.WHITE)


if __name__ == "__main__":
    main()
