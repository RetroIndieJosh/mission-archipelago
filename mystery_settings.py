import os
import yaml
from colorama import Fore

class MysterySettings(dict):
    """Stores game weights/counts and loaded game options."""
    def __init__(self, generation):
        super().__init__()
        self["game"] = {}
        self.games_data = {}
        self.generation = generation  # "count" or "weights"

    def add_game(self, game_path, key=None):
        """
        Add game metadata from YAML.
        key: optional dictionary key (aligns with config), defaults to filename.
        """
        if not game_path.endswith(".yaml"):
            return

        with open(game_path, encoding="utf-8-sig") as f:
            payload = yaml.safe_load(f) or {}

        filename_key = os.path.splitext(os.path.basename(game_path))[0]
        game_key = key or filename_key
        options = payload.copy()

        # Flatten nested key if exists
        if filename_key in options and isinstance(options[filename_key], dict):
            options = options[filename_key]
        options.pop(filename_key, None)

        # Ensure "name" exists in the options for downstream use
        if "name" not in options:
            options["name"] = "Player-{player}"
            print(Fore.YELLOW + f"Warning: 'name' key missing for game `{filename_key}`, using fallback '{options['name']}'" + Fore.WHITE)

        # Store metadata keyed by config/game key
        self.games_data[game_key] = {
            "file_path": game_path,
            "options": options.copy(),  # now guaranteed to have "name"
            "name": options["name"],    # convenient reference
            "description": options.get("description", ""),
            "requires": options.get("requires", {}),
        }

        # Initialize RAW if not already set
        if game_key not in self["game"]:
            if self.generation == "weights":
                self["game"][game_key] = options.get("weight", 1)
            else:
                self["game"][game_key] = options.get("count", 0)

    def __str__(self):
        lines = []
        if self.generation == "count":
            header = f"{'GAME':<30}{'#':>8}{'%':>6}\n" + "-"*44
            total = sum(w for g, w in self["game"].items() if w != 0)
            for game in sorted(self["game"]):
                raw = self["game"][game]
                if raw == 0:
                    continue
                pct = (raw / total) * 100 if total else 0
                # Table now uses the game key, not the YAML "name"
                lines.append(f"{game:<30}{raw:>8}{pct:>6.1f}%")
            table = header + "\n" + "\n".join(lines)
            table += f"\nTotal count: {total}"
        else:
            header = f"{'GAME':<30}{'RAW':>8}{'MOD':>8}{'%':>6}\n" + "-"*52
            total = sum(self["game"].values()) or 1
            for game in sorted(self["game"]):
                raw = self["game"][game]
                pct = (raw / total) * 100
                # Table now uses the game key, not the YAML "name"
                lines.append(f"{game:<30}{raw:>8}{raw:>8}{pct:>6.1f}%")  # MOD = RAW
            table = header + "\n" + "\n".join(lines)
            total_mod = sum(self["game"].values())
            table += f"\nTotal weight: {total_mod}"

        return table
