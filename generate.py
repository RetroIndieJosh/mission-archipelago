import os
import random
import sys
from collections import Counter

from config_loader import load_config
from mystery_settings import MysterySettings
from file_utils import collect_game_files, write_outputs


def _config_path_from_argv(default: str = "async.yaml") -> str:
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            return arg
    return default


def _has_flag(flag: str) -> bool:
    return flag in sys.argv[1:]


def main(config_path: str | None = None, output_dir: str = "output") -> None:
    if config_path is None:
        config_path = _config_path_from_argv()

    dry_run = _has_flag("--dry")

    cfg, world_mult, world_mult_range, total_games, seed = load_config(config_path)

    # ---------------- RNG seeding ----------------
    if seed > 0:
        random.seed(seed)
        actual_seed = seed
    else:
        actual_seed = random.randrange(1 << 32)
        random.seed(actual_seed)

    mystery = MysterySettings()
    game_cfg = cfg.get("game", {})

    # --------------------------------------------------
    # MODE 1: weighted selection to exact total-games
    # --------------------------------------------------
    if total_games > 0:
        games = list(game_cfg.keys())
        weights = [int(game_cfg[g]) for g in games]

        chosen = random.choices(games, weights=weights, k=total_games)
        counts = Counter(chosen)

        for g in games:
            mystery["game"][g] = counts.get(g, 0)

    # --------------------------------------------------
    # MODE 2: direct counts with world-mult logic
    # --------------------------------------------------
    else:
        for gname, val in game_cfg.items():
            if world_mult_range > 0:
                mult = random.randint(world_mult, world_mult + world_mult_range)
            else:
                mult = world_mult

            mystery["game"][gname] = int(val) * mult

    # Load game metadata
    for path in collect_game_files():
        filename_key = os.path.splitext(os.path.basename(path))[0]
        key = filename_key if filename_key in mystery["game"] else None
        mystery.add_game(path, key=key)

    if dry_run:
        print("\n[DRY RUN — no files written]\n")
    else:
        write_outputs(mystery, output_dir=output_dir)

    print("\nEstimated game distribution:\n")
    print(mystery)

    if seed == 0:
        print(f"\nSeed used: {actual_seed}")


if __name__ == "__main__":
    main()
