from typing import Any, Dict, Tuple

import yaml
from colorama import Fore


class ConfigError(Exception):
    pass


def load_config(path: str = "async.yaml") -> Tuple[
    Dict[str, Any], int, int, int, int, str | None
]:
    """
    Returns:
        cfg
        world_mult
        world_mult_range
        total_games
        seed
        ffr_path
    """
    try:
        with open(path, encoding="utf-8-sig") as cf:
            cfg = yaml.safe_load(cf) or {}
    except FileNotFoundError:
        print(Fore.RED + f"Config `{path}` not found." + Fore.WHITE)
        raise ConfigError
    except yaml.YAMLError as e:
        print(Fore.RED + f"YAML parse error in `{path}`: {e}" + Fore.WHITE)
        raise ConfigError

    def _int(name: str, default: int = 0) -> int:
        val = cfg.get(name, default)
        try:
            val = int(val)
        except (TypeError, ValueError):
            print(Fore.RED + f"'{name}' must be an integer." + Fore.WHITE)
            raise ConfigError
        if val < 0:
            print(Fore.RED + f"'{name}' must be >= 0." + Fore.WHITE)
            raise ConfigError
        return val

    world_mult = _int("world-mult", 1)
    world_mult_range = _int("world-mult-range", 0)
    total_games = _int("total-games", 0)

    # ---- seed (hex or int) ----
    raw_seed = cfg.get("seed", 0)
    try:
        if isinstance(raw_seed, str):
            seed = int(raw_seed, 0)
        else:
            seed = int(raw_seed)
    except (TypeError, ValueError):
        print(Fore.RED + "'seed' must be hex (0x...) or integer." + Fore.WHITE)
        raise ConfigError

    if seed < 0 or seed > 0x100000000:
        print(
            Fore.RED
            + "seed must be in range 0x1–0x100000000 (0 means random)."
            + Fore.WHITE
        )
        raise ConfigError

    ffr_path = cfg.get("FFR")
    if ffr_path is not None and not isinstance(ffr_path, str):
        print(Fore.RED + "'FFR' must be a path string." + Fore.WHITE)
        raise ConfigError

    return cfg, world_mult, world_mult_range, total_games, seed, ffr_path
