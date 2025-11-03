# Mission Archipelago
Multiworld yaml generator for [Archipelago](www.archipelago.gg) asyncs run by
[Retro Indie Josh](retroindiejosh.itch.io). Props to [Async
Tools](https://github.com/ArchipelagoMW/AsyncTools) for giving me a starting
point.

## Usage
1. update `ap-async.bat` with paths to your AP install (PLAYERS and WORLDS)
1. Modify `async.yaml` with your desired settings and weights (options
documented in the included file)
1. Run `gen-async.bat` to generate the AP yaml files for the async
1. Run `ap-async.bat` to generate the worlds in your AP "output" directory

## Notes
When using weights, Archipelago guarantees every game gets at least one seed,
even if the weight is 0 or the requested player count is lower than the number
of possible players

## YAML Changes Under Consideration

### DOOM 1993 / DOOM II
- Find a more interesting way to do only boss levels: Unlock all non boss levels
(plus keys) from the start? Make boss level unlocks local so they need to be
found within the game itself? Ensure boss level items are junk so they aren't
part of a larger chain (and especially don't hide guns)?
- Start with all levels, or start with all keys: See if either of these options
remain interesting while being slightly less frustratingly slow to unlock

### Ocarina of Time
- When the bridge requires one medallion or one stone, ensure that the opposite type is given: Is this even possible? There are options for nonlocal rewards/medallions/stones but I dunno what that does since you can't shuffle them in this version
- Start with bunny hood if Complete Mask Quest is true: doesn't seem possible until we get the new version of OoTR that has starting with Zelda's Letter

### Subnautica
- Make it more closed for longer: Not sure how to fix this, but particularly at higher difficulty depths, the game opens up the entire overworld map (and some of the underworld) as soon as you find the local seaglide pieces

## TODO - BUGS
- fails in weights mode because weights.yaml isn't set up correctly

## TODO - FEATURES
- separate async.yaml (settings) from game-weights.yaml (game weights - won't
need top level "game" key anymore)
- verify minimum versions in game yamls
- update ap-gen.bat to default to 1 multiworld if just press enter (blank)
- don't generate weights.yaml in count mode
- update ap-gen.bat to use weights if weights.yaml exists, count otherwise
- override switches in generate such as --mode weights, --mode count, --max-rank 3
- output final data table as csv (possible --csv option)
- fix categorize: rank, max rank, and rank mult (will require determining and retaining rank for each game, instead of flattening the directory structure and ignoring it)
- detect number of games generated from AP output when using weight mode and print a summary at the end
- setup script or on a first run of gen-async.bat asking for path to AP install so gen-async.bat doesn't require manual modification (and some mechanics to reset to change)