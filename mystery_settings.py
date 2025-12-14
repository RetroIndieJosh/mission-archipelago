import os
from typing import Any, Dict

import yaml
from colorama import Fore


class MysterySettings(dict):
    def __init__(self) -> None:
        super().__init__()
        self["game"]: Dict[str, int] = {}
        self.games_data: Dict[str, Dict[str, Any]] = {}

    def add_game(self, game_path: str, key: str | None = None) -> None:
        if not game_path.endswith(".yaml"):
            return

        with open(game_path, encoding="utf-8-sig") as f:
            payload = yaml.safe_load(f) or {}

        filename_key = os.path.splitext(os.path.basename(game_path))[0]
        game_key = key or filename_key

        options = dict(payload)

        if (
            len(options) == 1
            and filename_key in options
            and isinstance(options[filename_key], dict)
        ):
            options = dict(options[filename_key])

        if "name" not in options:
            options["name"] = "Player-{player}"
            print(
                Fore.YELLOW
                + f"Warning: 'name' missing for `{filename_key}`, using fallback."
                + Fore.WHITE
            )

        self.games_data[game_key] = {
            "file_path": game_path,
            "options": dict(options),
            "name": options["name"],
            "description": options.get("description", ""),
            "requires": dict(options.get("requires", {})),
        }

        if game_key not in self["game"]:
            self["game"][game_key] = 0

    def build_game_export(self, game_key: str) -> Dict[str, Any]:
        from copy import deepcopy

        info = self.games_data[game_key]
        options = deepcopy(info["options"])

        for meta in ("name", "description", "requires"):
            options.pop(meta, None)

        return {
            "game": game_key,
            "name": info["name"],
            "description": info["description"],
            "requires": info["requires"],
            game_key: options,
        }

    def __str__(self) -> str:
        lines = []
        total = sum(v for v in self["game"].values() if v > 0)
        unique = sum(1 for v in self["game"].values() if v > 0)

        header = f"{'GAME':<30}{'#':>8}{'%':>6}\n" + "-" * 46

        for game in sorted(self["game"]):
            count = self["game"][game]
            if count == 0:
                continue
            pct = (count / total) * 100 if total else 0
            lines.append(f"{game:<30}{count:>8}{pct:>6.1f}%")

        table = header + "\n" + "\n".join(lines)
        table += f"\nUnique games: {unique}"
        table += f"\nTotal count: {total}"
        return table
