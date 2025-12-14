import os
import random
import sys
from collections import Counter

from config_loader import load_config
from mystery_settings import MysterySettings
from file_utils import collect_game_files, write_outputs


def _parse_args(default_config: str = "async.yaml"):
    """
    Parses command-line arguments.

    Returns:
        config_path (str)
        total_games_override (int | None)
        dry_run (bool)
    """
    config_path = default_config
    total_games_override = None
    dry_run = False

    for arg in sys.argv[1:]:
        if arg == "--dry":
            dry_run = True
        elif arg.isdigit():
            if total_games_override is None:
                total_games_override = int(arg)
        elif not arg.startswith("--"):
            config_path = arg

    return config_path, total_games_override, dry_run


def main(output_dir: str = "output") -> None:
    config_path, total_games_override, dry_run = _parse_args()

    cfg, world_mult, world_mult_range, total_games, seed = load_config(config_path)

    # ---------------- RNG seeding ----------------
    if seed > 0:
        random.seed(seed)
        actual_seed = seed
    else:
        actual_seed = random.randrange(1 << 32)
        random.seed(actual_seed)

    # ---------------- CLI override ----------------
    if total_games_override is not None:
        total_games = total_games_override

    if total_games > 0 and (world_mult > 0 or world_mult_range > 0):
        print(
            "[note] total-games is set; "
            "world-mult and world-mult-range are ignored."
        )

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

