# Mission Archipelago

Multiworld yaml generator for [Archipelago](www.archipelago.gg) asyncs run by [Retro Indie Josh](retroindiejosh.itch.io). Props to [Async Tools](https://github.com/ArchipelagoMW/AsyncTools) for giving me a starting point.

## Usage

1. update `ap-async.bat` with paths to your AP install (PLAYERS and WORLDS)

1. Modify `async.yaml` with your desired settings and weights (options documented in the included file)
1. Run `gen-async.bat` to generate the AP yaml files for the async
1. Run `ap-async.bat` to generate the worlds in your AP "output" directory

## TODO
- Archipelago does in fact guarantee each game gets one seed when you use weights
    - (I'm leaving this here so I don't forget)