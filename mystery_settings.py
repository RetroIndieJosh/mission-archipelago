import os
import yaml
from colorama import Fore

class MysterySettings(dict):
    """Stores game weights/counts and loaded game options."""
    def __init__(self, generation, max_rank=1, rank_mult=1.0):
        super().__init__()
        self["game"] = {}
        self.games_data = {}
        self.generation = generation
        self.max_rank = max_rank
        self.rank_mult = rank_mult
        self.rank_mod = {}

    def add_game(self, game_path):
        if not game_path.endswith(".yaml"):
            return

        print(f"Loading {game_path}...")
        with open(game_path, encoding="utf-8-sig") as f:
            payload = yaml.safe_load(f) or {}

        game = os.path.splitext(os.path.basename(game_path))[0]
        options = payload.copy()

        # flatten nested key if exists
        if game in options and isinstance(options[game], dict):
            options = options[game]
        options.pop(game, None)

        game_name_value = options.get("name")
        if game_name_value is None:
            game_name_value = "Player-{player}"
            print(Fore.YELLOW + f"Warning: 'name' key missing for game `{game}`, using fallback '{game_name_value}'" + Fore.WHITE)

        self.games_data[game] = {
            "options": options.copy(),
            "name": game_name_value,
            "description": options.get("description", ""),
            "requires": options.get("requires", {}),
        }

    def compute_rank_mods(self):
        if self.generation != "weights":
            return
        for game, raw in self["game"].items():
            # Example: rank based on alphabetical order
            rank = sorted(self["game"].keys()).index(game) + 1
            mod = raw * (self.rank_mult ** (self.max_rank - rank))
            self.rank_mod[game] = int(mod + 0.9999)  # ceiling

    def __str__(self):
        # Build table with RAW / MOD / % / RANK
        header = "GAME                            RAW      MOD        %     RANK\n"
        header += "-" * 60 + "\n"
        total = sum(self.rank_mod.get(g, w) if self.generation=="weights" else w for g,w in self["game"].items()) or 1
        lines = []
        for game in sorted(self["game"]):
            raw = self["game"][game]
            mod = self.rank_mod.get(game, raw)
            pct = (mod / total) * 100
            rank = sorted(self["game"].keys()).index(game) + 1
            lines.append(f"{game:<30} {raw:<8} {mod:<8} {pct:>6.1f}% {rank:>4}")
        return header + "\n".join(lines)
