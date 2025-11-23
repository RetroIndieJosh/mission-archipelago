import yaml
from colorama import Fore
import sys

def load_config(path):
    try:
        with open(path, encoding="utf-8-sig") as cf:
            cfg = yaml.safe_load(cf) or {}
    except FileNotFoundError:
        print(Fore.RED + f"Config `{path}` not found." + Fore.WHITE)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(Fore.RED + f"YAML parse error in config `{path}`: {e}" + Fore.WHITE)
        sys.exit(2)

    # Determine generation
    generation = cfg.get("generation", "weights")
    if generation not in ("weights", "count"):
        print(Fore.RED + "generation must be 'weights' or 'count'." + Fore.WHITE)
        sys.exit(2)

    # Max rank for rank mode
    max_rank = cfg.get("max-rank", 1)

    # Rank multiplier
    rank_mult = cfg.get("rank-mult")
    if rank_mult is None:
        print(Fore.YELLOW + "Warning: 'rank-mult' not defined; rank will not affect weights." + Fore.WHITE)
        rank_mult = 1.0

    return cfg, generation, max_rank, rank_mult
