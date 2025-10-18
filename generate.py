import os
import yaml

from colorama import Fore
from pprint import pprint

class MysterySettings(dict):
    def __init__(self, name: str, description: str, requires: dict, game: dict):
        super().__init__()

        self["name"] = name
        self["description"] = description
        self["requires"] = requires
        self["game"] = game

    def __str__(self) -> str:
        string = "{:<32} {:<4} {:>8}\n".format("GAME", "WGT", "%")
        string += "-" * 46
        string += "\n"
        for game, percentage in sorted(self.weight_percentages().items(), key=lambda x:x[1], reverse=True):
            string += "{:<32} {:<4}  ~{:>6}\n".format(game, self["game"][game], "{:.1f}%".format(percentage * 100))

        return string

    def add_game(self, game_path: str):
        if not game_path.endswith(".yaml"):
            print(f"Skipping `{game_path}` because it's not game settings")
            return
        try:
            print(f"Loading {game_path}...")
            with open(game_path, encoding="utf-8-sig") as game_file:
                game_settings: dict = yaml.unsafe_load(game_file)

                # Ensure that game_settings only has one property which has the same name as the file.
                if len(game_settings.items()) > 1:
                    raise ValueError(f"Found {len(game_settings)} top-level keys in `{game_path}`")
                
                game = next(iter(game_settings))
                if game not in game_settings:
                    raise ValueError(f"Could not find `{game}` top-level key in `{game_path}`")

                self.update(game_settings)
        except FileNotFoundError:
            print(Fore.RED + f"\nUnable to find game settings file `{game_path}`." + Fore.WHITE)
            exit(1)
        except ValueError as e:
            print(Fore.RED + f"\nGame settings dict should only have 1 key named after the game.\n\t{e}" + Fore.WHITE)
            exit(2)
        meta_path = os.path.join("games", f"{game}.meta.yaml")
        if os.path.exists(meta_path):
            with open(meta_path) as meta_file:
                meta_settings: dict = yaml.unsafe_load(meta_file)
            if len(meta_settings.items()) > 1:
                raise ValueError(f"Found {len(meta_settings)} top-level keys in `{meta_path}`")
            if game not in meta_settings:
                raise ValueError(f"Could not find `{game}` top-level key in `{meta_path}`")
            meta.update(meta_settings)

    def total_game_weights(self) -> int:
        total = 0
        for weight in self["game"].values():
            total += weight
        return total

    def weight_percentages(self) -> dict:
        total = self.total_game_weights()
        games = {}

        for game, weight in self["game"].items():
            games[game] = weight / total

        return games


class GameSettings(MysterySettings):
    def __init__(self, name: str, description: str, requires: dict, game: str, game_options: dict):
        super().__init__(name, description, requires, game)

        self[game] = game_options


def main():
    # Create output directory, if it does not exist.
    if not os.path.exists("output/"):
        os.mkdir("output/")

    # Delete any old mystery.yaml file, if it exists.
    if os.path.exists("output/mystery.yaml"):
        os.remove("output/mystery.yaml")

    # Load meta data first.
    mystery: dict
    meta: dict = {
        "meta_description": "Generated from RetroIndieJosh's Mission Archipelago",
        None: {
            "progression_balancing": 0,
        }
    }
    print("Loading meta player settings...")
    try:
        with open("async.yaml") as file:
            data = yaml.unsafe_load(file)
            mystery = MysterySettings(data["name"], data["description"], data["requires"], data["game"])
    except FileNotFoundError:
        print(Fore.RED + "async.yaml not found. Please ensure file exists and rerun generator." + Fore.WHITE)
        exit(3)

    print(f"Estimated chance of a particular game being rolled...\n\n{mystery}")
    print("Attempting to generate yaml file...")

    # Merge together each game yaml into our mystery settings.
    # TODO pass in as an arg
    max_rank = 5
    for rank in range(1, max_rank+1):
        rank_path = f"./settings/Rank {rank}"
        for game_file in os.listdir(rank_path):
            mystery.add_game(f"{rank_path}/{game_file}")
        
    # I don't know where it generates this original list of games so we're just
    # going to remove the non matching ones here for now
    mystery["game"] = [g for g in list(mystery["game"]) if g in mystery.keys()]

    with open("output/weights.yaml", "w+") as file:
        yaml.dump(dict(mystery), file)
    with open("output/games.yaml", "w+") as file:
        games = list(mystery["game"])
        last_key = games[-1]
        for game in games:
            game_options = GameSettings(mystery["name"], mystery["description"], mystery["requires"], game, mystery[game])
            yaml.dump(dict(game_options), file)
            if game != last_key:
                file.write("\n---\n\n")
    print(Fore.GREEN + "\nOutput settings file to `./output/weights.yaml`")
    meta_path = os.path.join("output", "meta.yaml")
    with open(meta_path, "w+") as file:
        yaml.dump(meta, file)
    print(Fore.GREEN + f"\nOutput meta file to `{meta_path}`" + Fore.WHITE)

if __name__ == "__main__":
    main()
