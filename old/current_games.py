
_games = {}
# with open(r'assets/data/games.json') as f:
#     _games = json.load(f)

def read() -> dict:
    return _games

def write(key, value, edit=False) -> None:
    if key in _games:
        if not edit:
            raise KeyError("Key already exists. If u expected this make edit=True.")
        
    _games[key] = value

def rewrite(dict_) -> None:
    _games = dict_
