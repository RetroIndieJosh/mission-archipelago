from config_loader import load_config
from mystery_settings import MysterySettings
from file_utils import collect_game_files, write_outputs

def main():
    # Load configuration
    cfg, generation, *_ = load_config()  # ignore max_rank, rank_mult
    mystery = MysterySettings(generation)

    # Initialize RAW values from config
    for gname, val in cfg.get("game", {}).items():
        mystery["game"][gname] = int(val)

    # Add game metadata from YAML files
    game_files = collect_game_files()
    for f in game_files:
        # Align YAML with config key if it exists
        filename_key = f.split("/")[-1].split("\\")[-1].rsplit(".", 1)[0]
        key = filename_key if filename_key in mystery["game"] else None
        mystery.add_game(f, key=key)

    # Write outputs (unchanged)
    write_outputs(mystery, generation)

    print("\nEstimated game distribution:\n")
    print(mystery)

if __name__ == "__main__":
    main()
