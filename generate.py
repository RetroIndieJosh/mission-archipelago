import os
import random
import shutil
import sys
from collections import Counter

from config_loader import load_config
from mystery_settings import MysterySettings
from file_utils import collect_game_files, write_outputs


def _parse_args(default_config: str = "async.yaml"):
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

    # ---- clean output directory ----
    if not dry_run:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    (
        cfg,
        world_mult,
        world_mult_range,
        total_games,
        seed,
        ffr_path,
    ) = load_config(config_path)

    # ---- RNG seed ----
    if seed > 0:
        random.seed(seed)
        actual_seed = seed
    else:
        actual_seed = random.randrange(1 << 32)
        random.seed(actual_seed)

    if total_games_override is not None:
        total_games = total_games_override

    mystery = MysterySettings()
    game_cfg = cfg.get("game", {})

    # ---- counts ----
    if total_games > 0:
        games = list(game_cfg.keys())
        weights = [int(game_cfg[g]) for g in games]

        chosen = random.choices(games, weights=weights, k=total_games)
        counts = Counter(chosen)

        for g in games:
            mystery["game"][g] = counts.get(g, 0)
    else:
        for g, val in game_cfg.items():
            if world_mult_range > 0:
                mult = random.randint(world_mult, world_mult + world_mult_range)
            else:
                mult = world_mult
            mystery["game"][g] = int(val) * mult

    # ---- load metadata ----
    for path in collect_game_files():
        key = os.path.splitext(os.path.basename(path))[0]
        key = key if key in mystery["game"] else None
        mystery.add_game(path, key=key)

    # ---- FFR validation ----
    ffr_files = []
    ff_game = "Final Fantasy"

    if mystery["game"].get(ff_game, 0) > 0:
        mystery.mark_external(ff_game)

        if not ffr_path:
            print("Final Fantasy selected but FFR path not provided.")
            sys.exit(1)

        if not os.path.isdir(ffr_path):
            print(f"FFR path does not exist: {ffr_path}")
            sys.exit(1)

        yamls = sorted(
            f for f in os.listdir(ffr_path) if f.lower().endswith(".yaml")
        )

        if len(yamls) != mystery["game"][ff_game]:
            print(
                f"FFR YAML count mismatch: expected "
                f"{mystery['game'][ff_game]}, found {len(yamls)}"
            )
            sys.exit(1)

        for y in yamls:
            base = os.path.splitext(y)[0]
            nes = base + ".nes"
            if not os.path.isfile(os.path.join(ffr_path, nes)):
                print(f"Missing matching NES for {y}")
                sys.exit(1)
            ffr_files.append((y, nes))

    if dry_run:
        print("\n[DRY RUN — no files written]\n")
    else:
        write_outputs(mystery, output_dir=output_dir)

        for i, (y, nes) in enumerate(ffr_files, start=1):
            # copy + rename YAML
            src_yaml = os.path.join(ffr_path, y)
            dst_yaml = os.path.join(output_dir, f"{ff_game}_{i}.yaml")
            with open(src_yaml, "rb") as fsrc, open(dst_yaml, "wb") as fdst:
                fdst.write(fsrc.read())

            # copy + rename NES
            src_nes = os.path.join(ffr_path, nes)
            dst_nes = os.path.join(output_dir, f"{ff_game}_{i}.nes")
            with open(src_nes, "rb") as fsrc, open(dst_nes, "wb") as fdst:
                fdst.write(fsrc.read())

    print("\nEstimated game distribution:\n")
    print(mystery)

    if ffr_files:
        meta_path = os.path.join(output_dir, "ffr.meta")
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(f"count={len(ffr_files)}\n")

    print(f"seed={actual_seed}")
    print(f"count={len(ffr_files)}")


if __name__ == "__main__":
    main()
