# Kivi-Paperi-Sakset (Poetry + Flask)

## Prerequisites
- Python 3.12+
- Poetry (for dependency management)

## Install
```bash
poetry install
```

## Run the web UI
```bash
poetry run flask --app src.web_app run --port 5000
```
- Open http://localhost:5000 to play.
- Optional: set an environment secret for sessions
```bash
export FLASK_SECRET_KEY="some-random-string"
```

## CLI version (existing)
```bash
poetry run python src/index.py
```

## Notes
- Game state is stored in memory per browser session; restarting the server clears it.
- Valid moves: k, p, s. The game stops when an invalid move is entered.
