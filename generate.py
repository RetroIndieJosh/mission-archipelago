from config_loader import load_config
from mystery_settings import MysterySettings
from file_utils import collect_game_files, write_outputs

def main():
    cfg, generation, max_rank, rank_mult = load_config()
    mystery = MysterySettings(generation, max_rank, rank_mult)

    for gname, val in cfg["game"].items():
        mystery["game"][gname] = int(val)

    game_files = collect_game_files()
    for f in game_files:
        mystery.add_game(f)

    mystery.compute_rank_mods()
    write_outputs(mystery, generation)

    print("\nEstimated game distribution:\n")
    print(mystery)

if __name__ == "__main__":
    main()
