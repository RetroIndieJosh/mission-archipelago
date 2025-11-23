import os
from typing import Any, Dict

import yaml
from colorama import Fore


class MysterySettings(dict):
    """Stores game weights/counts and loaded game options."""

    def __init__(self, generation: str) -> None:
        super().__init__()
        self["game"]: Dict[str, int] = {}
        self.games_data: Dict[str, Dict[str, Any]] = {}
        self.generation: str = generation  # "count" or "weights"

    # ------------------------------------------------------------------ #
    # Loading games
    # ------------------------------------------------------------------ #
    def add_game(self, game_path: str, key: str | None = None) -> None:
        """Add game metadata and options from a YAML file."""
        if not game_path.endswith(".yaml"):
            return

        with open(game_path, encoding="utf-8-sig") as f:
            payload = yaml.safe_load(f) or {}

        filename_key = os.path.splitext(os.path.basename(game_path))[0]
        game_key = key or filename_key

        options = dict(payload)

        # If the file is shaped like: { filename_key: { ... } }, flatten it.
        if (
            len(options) == 1
            and filename_key in options
            and isinstance(options[filename_key], dict)
        ):
            options = dict(options[filename_key])

        # Fallback name if missing
        if "name" not in options:
            options["name"] = "Player-{player}"
            print(
                Fore.YELLOW
                + f"Warning: 'name' key missing for game `{filename_key}`, "
                  "using fallback '{options['name']}'"
                + Fore.WHITE
            )

        description = options.get("description", "")
        requires_raw = options.get("requires", {})

        # Normalize requires to a dict (avoid weird payload types bleeding through)
        if not isinstance(requires_raw, dict):
            print(
                Fore.YELLOW
                + f"Warning: 'requires' for `{game_key}` should be a mapping; "
                  "treating as empty."
                + Fore.WHITE
            )
            requires = {}
        else:
            requires = dict(requires_raw)

        self.games_data[game_key] = {
            "file_path": game_path,
            "options": dict(options),
            "name": options["name"],
            "description": description,
            "requires": requires,
        }

        # Initialize weight/count if config didn't explicitly specify one.
        if game_key not in self["game"]:
            if self.generation == "weights":
                self["game"][game_key] = int(options.get("weight", 1))
            else:
                self["game"][game_key] = int(options.get("count", 1))

    # ------------------------------------------------------------------ #
    # Export helpers
    # ------------------------------------------------------------------ #
    def build_game_export(self, game_key: str) -> Dict[str, Any]:
        """
        Build the final export payload for a single game.

        Strips internal metadata from options and returns a dict shaped like:
        {
            "game": game_key,
            "name": ...,
            "description": ...,
            "requires": {...},
            game_key: { ... sanitized options ... }
        }
        """
        from copy import deepcopy

        if game_key not in self.games_data:
            raise KeyError(f"Unknown game key: {game_key!r}")

        info = self.games_data[game_key]

        options_copy = deepcopy(info["options"])

        # If options already has the game as a top-level key, extract inner dict.
        if game_key in options_copy and isinstance(options_copy[game_key], dict):
            options_copy = options_copy[game_key]

        # Remove metadata keys from options
        for meta_key in ("name", "description", "requires"):
            options_copy.pop(meta_key, None)

        requires_copy = deepcopy(info["requires"])

        return {
            "game": game_key,
            "name": info["name"],
            "description": info["description"],
            "requires": requires_copy,
            game_key: options_copy,
        }

    # ------------------------------------------------------------------ #
    # Representation
    # ------------------------------------------------------------------ #
    def __str__(self) -> str:
        lines: list[str] = []

        if self.generation == "count":
            header = f"{'GAME':<30}{'#':>8}{'%':>6}\n" + "-" * 44
            total = sum(w for w in self["game"].values() if w != 0)
            for game in sorted(self["game"]):
                raw = self["game"][game]
                if raw == 0:
                    continue
                pct = (raw / total) * 100 if total else 0.0
                lines.append(f"{game:<30}{raw:>8}{pct:>6.1f}%")
            table = header + "\n" + "\n".join(lines)
            table += f"\nTotal count: {total}"
        else:
            # Weights mode: show raw weights and percentages
            header = f"{'GAME':<30}{'RAW':>8}{'%':>6}\n" + "-" * 46
            total = sum(self["game"].values()) or 1
            for game in sorted(self["game"]):
                raw = self["game"][game]
                pct = (raw / total) * 100
                lines.append(f"{game:<30}{raw:>8}{pct:>6.1f}%")
            table = header + "\n" + "\n".join(lines)
            table += f"\nTotal weight: {total}"

        return table
