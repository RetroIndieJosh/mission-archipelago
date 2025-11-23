import sys
sys.path.append("..")

import mystery_settings as mod


def test_add_game_flat(tmp_yaml):
    yaml_file = tmp_yaml("foo.yaml", {
        "name": "Test Game",
        "weight": 5,
        "optionA": True
    })

    ms = mod.MysterySettings("weights")
    ms.add_game(str(yaml_file))

    assert "foo" in ms.games_data
    assert ms.games_data["foo"]["name"] == "Test Game"
    assert ms["game"]["foo"] == 5
    assert ms.games_data["foo"]["options"]["optionA"] is True


def test_add_game_nested(tmp_yaml):
    yaml_file = tmp_yaml("bar.yaml", {
        "bar": {
            "name": "Nested Game",
            "count": 2,
            "setting": 123
        }
    })

    ms = mod.MysterySettings("count")
    ms.add_game(str(yaml_file))

    assert ms.games_data["bar"]["name"] == "Nested Game"
    assert ms["game"]["bar"] == 2
    assert ms.games_data["bar"]["options"]["setting"] == 123


def test_add_game_missing_name(tmp_yaml):
    yaml_file = tmp_yaml("no_name.yaml", {"x": 1})

    ms = mod.MysterySettings("weights")
    ms.add_game(str(yaml_file))

    assert ms.games_data["no_name"]["name"] == "Player-{player}"


def test_str_weights():
    ms = mod.MysterySettings("weights")
    ms["game"] = {"a": 2, "b": 3}

    out = str(ms)
    assert "RAW" in out
    assert "Total weight: 5" in out
