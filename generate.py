import os
import sys
import argparse
import yaml
from colorama import Fore
from math import ceil


class MysterySettings(dict):
    """Hold configured weights/counts and per-game loaded data."""

    def __init__(self, generation: str, max_rank=1, rank_mult=1.0):
        super().__init__()
        self["game"] = {}  # mapping game_name -> weight/count
        self.generation = generation
        self.games_data = {}  # mapping game_name -> {"options":..., "name":..., "description":..., "requires":...}
        self.game_rank = {}  # mapping game_name -> rank
        self.max_rank = max_rank
        self.rank_mult = rank_mult

    def __str__(self) -> str:
        lines = []
        if self.generation == "weights":
            print(f"Rank multiplier: {self.rank_mult}\n")
        header_label = "RAW"
        col_names = ["GAME", header_label, "MOD", "%", "RANK"] if self.game_rank else ["GAME", header_label, "MOD", "%"]
        if self.game_rank:
            header = "{:<32} {:<6} {:<6} {:>8} {:<6}\n".format(*col_names)
        else:
            header = "{:<32} {:<6} {:<6} {:>8}\n".format(*col_names[:-1])
        lines.append("-" * 78)

        # calculate total modified weight for percentage
        total_mod = sum(
            ceil(self["game"][g] * (self.rank_mult ** (self.max_rank - self.game_rank.get(g, 0))))
            if self.generation == "weights" and g in self.game_rank else self["game"][g]
            for g in self["game"]
        )

        for game in sorted(self["game"], key=lambda x: self["game"][x], reverse=True):
            raw = int(self["game"][game])
            rank = self.game_rank.get(game, None)
            if self.generation == "weights" and rank is not None:
                mod_val = raw * (self.rank_mult ** (self.max_rank - rank))
            else:
                mod_val = raw
            mod_val = ceil(mod_val)
            pct = (mod_val / total_mod * 100) if total_mod > 0 else 0
            if rank is not None:
                lines.append("{:<32} {:<6} {:<6} {:>7.1f}% {:<6}".format(game, raw, mod_val, pct, rank))
            else:
                lines.append("{:<32} {:<6} {:<6} {:>7.1f}%".format(game, raw, mod_val, pct))

        return header + "\n" + "\n".join(lines)

    def add_game(self, game_path: str, rank=None):
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

        # Flatten nested key if present
        if game in options and isinstance(options[game], dict):
            options = options[game]
        options.pop(game, None)

        # name fallback
        game_name_value = options.get("name", None)
        if game_name_value is None:
            game_name_value = "Player-{player}"
            print(Fore.YELLOW + f"Warning: 'name' key missing for game `{game}`, using fallback '{game_name_value}'" + Fore.WHITE)

        self.games_data[game] = {
            "options": options.copy(),
            "name": game_name_value,
            "description": options.get("description", ""),
            "requires": options.get("requires", {}),
        }

        if rank is not None:
            self.game_rank[game] = rank

    def total_game_weights(self) -> int:
        return sum(int(v) for v in self["game"].values())


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

    max_rank = cfg.get("max-rank", 1)
    rank_mult = cfg.get("rank-mult", None)
    if rank_mult is None:
        print(Fore.YELLOW + "rank-mult not defined; rank will not affect weights." + Fore.WHITE)
        rank_mult = 1.0

    if cat == "rank" and (not isinstance(max_rank, int) or max_rank < 1):
        print(Fore.RED + "Missing or invalid `max-rank` for rank categorization." + Fore.WHITE)
        sys.exit(3)

    if not isinstance(cfg["game"], dict):
        print(Fore.RED + "`game` top-level key must be a mapping of game->weight/count." + Fore.WHITE)
        sys.exit(3)

    return gen, cat, max_rank, float(rank_mult)


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
                    files.append((os.path.join(rank_dir, fn), r))
    else:  # all
        for root, _, fns in os.walk("settings"):
            for fn in fns:
                if fn.endswith(".yaml"):
                    files.append((os.path.join(root, fn), None))
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

    generation_mode, categorize, max_rank, rank_mult = validate_config(cfg)

    mystery = MysterySettings(generation_mode, max_rank, rank_mult)
    for gname, val in cfg["game"].items():
        try:
            w = int(val)
        except Exception:
            print(Fore.RED + f"Invalid weight/count for `{gname}`; must be integer-like." + Fore.WHITE)
            sys.exit(3)
        if w > 0:
            mystery["game"][str(gname)] = w

    game_files = collect_game_files(categorize, max_rank)
    print(f"Found {len(game_files)} game files.")
    for path, rank in game_files:
        mystery.add_game(path, rank)

    # discard configured games not present in loaded files
    mystery["game"] = {g: v for g, v in mystery["game"].items() if g in mystery.games_data}

    # prepare output directory
    os.makedirs("output", exist_ok=True)
    games_path = os.path.join("output", "games.yaml")

    # write games.yaml
    with open(games_path, "w", encoding="utf-8") as gf:
        for game, count in mystery["game"].items():
            reps = count if generation_mode == "count" else 1
            for _ in range(reps):
                options = mystery.games_data[game]["options"].copy()
                yaml.dump({game: options}, gf, sort_keys=False)
                gf.write("\n")
                metadata = {
                    "description": mystery.games_data[game]["description"],
                    "game": game,
                    "name": mystery.games_data[game]["name"],
                    "requires": mystery.games_data[game]["requires"],
                }
                yaml.dump(metadata, gf, sort_keys=False)
                gf.write("\n---\n\n")

    if generation_mode == "weights":
        weights_path = os.path.join("output", "weights.yaml")
        with open(weights_path, "w", encoding="utf-8") as wf:
            yaml.dump(dict(mystery), wf, sort_keys=False)

    # summary
    print(f"\nMode: generation={generation_mode}, categorize={categorize}")
    print(f"Estimated game distribution:\n\n{mystery}")
    print(Fore.GREEN + "\nOutput written to ./output/ directory" + Fore.WHITE)


if __name__ == "__main__":
    main()
