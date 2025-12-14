import sys
from typing import Any, Dict, Tuple

import yaml
from colorama import Fore

class ConfigError(Exception):
    pass


def load_config(path: str = "async.yaml") -> Tuple[Dict[str, Any], str, int, float]:
    """
    Load and validate the main configuration file.

    Returns:
        cfg:        The parsed configuration dictionary.
        generation: Either "weights" or "count".
        max_rank:   Reserved for future rank-based features (currently unused).
        rank_mult:  Reserved for future rank-based features (currently unused).
    """
    try:
        with open(path, encoding="utf-8-sig") as cf:
            cfg = yaml.safe_load(cf) or {}
    except FileNotFoundError:
        print(Fore.RED + f"Config `{path}` not found." + Fore.WHITE)
        raise ConfigError("message")

    except yaml.YAMLError as e:
        print(
            Fore.RED + f"YAML parse error in config `{path}`: {e}" + Fore.WHITE
        )
        raise ConfigError("message")


    # Determine generation mode
    generation = cfg.get("generation", "weights")
    if generation not in ("weights", "count"):
        print(Fore.RED + "generation must be 'weights' or 'count'." + Fore.WHITE)
        raise ConfigError("message")

    # These are preserved for compatibility but currently not used elsewhere.
    max_rank = int(cfg.get("max-rank", 1))

    rank_mult_value = cfg.get("rank-mult")
    if rank_mult_value is None:
        print(
            Fore.YELLOW
            + "Warning: 'rank-mult' not defined; rank will not affect weights."
            + Fore.WHITE
        )
        rank_mult = 1.0
    else:
        try:
            rank_mult = float(rank_mult_value)
        except (TypeError, ValueError):
            print(
                Fore.YELLOW
                + "Warning: 'rank-mult' must be numeric; defaulting to 1.0."
                + Fore.WHITE
            )
            rank_mult = 1.0

    world_mult_value = cfg.get("world-mult", 1)
    world_mult_range_value = cfg.get("world-mult-range", 0)

    try:
        world_mult = int(world_mult_value)
        world_mult_range = int(world_mult_range_value)
    except (TypeError, ValueError):
        print(Fore.RED + "'world-mult' and 'world-mult-range' must be integers." + Fore.WHITE)
        raise ConfigError("message")

    if world_mult < 0 or world_mult_range < 0:
        print(Fore.RED + "'world-mult' and 'world-mult-range' must be >= 0." + Fore.WHITE)
        raise ConfigError("message")

    return cfg, generation, max_rank, rank_mult, world_mult, world_mult_range
