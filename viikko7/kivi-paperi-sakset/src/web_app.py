import os
from uuid import uuid4
from flask import Flask, render_template_string, request, redirect, url_for, session
from tuomari import Tuomari
from tekoaly import Tekoaly
from tekoaly_parannettu import TekoalyParannettu
from kivi_paperi_sakset import WIN_TARGET

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

# In-memory game store keyed by a session id.
_games = {}


VALID_MOVES = {"k", "p", "s"}
MODE_LABELS = {
    "pvp": "Pelaaja vs pelaaja",
    "ai": "Pelaaja vs tekoäly",
    "ai_plus": "Pelaaja vs parannettu tekoäly",
}


def _current_game():
    """Return or create the game state associated with the browser session."""
    game_id = session.get("game_id")
    if not game_id or game_id not in _games:
        game_id = str(uuid4())
        session["game_id"] = game_id
        _games[game_id] = {
            "mode": None,
            "tuomari": Tuomari(),
            "ai": None,
            "history": [],
        }
    return _games[game_id]


def _reset_game(mode: str):
    game = _current_game()
    game["mode"] = mode
    game["tuomari"] = Tuomari()
    game["history"] = []
    if mode == "ai":
        game["ai"] = Tekoaly()
    elif mode == "ai_plus":
        game["ai"] = TekoalyParannettu(10)
    else:
        game["ai"] = None
    return game


def _status_text(tuomari: Tuomari) -> str:
    return str(tuomari).replace("\n", "<br>")


def _has_winner(tuomari: Tuomari) -> bool:
    return tuomari.ekan_pisteet >= WIN_TARGET or tuomari.tokan_pisteet >= WIN_TARGET


def _winner_text(tuomari: Tuomari) -> str | None:
    if tuomari.ekan_pisteet >= WIN_TARGET:
        return f"Ensimmäinen pelaaja voitti ({WIN_TARGET} voittoa)"
    if tuomari.tokan_pisteet >= WIN_TARGET:
        return f"Toinen pelaaja voitti ({WIN_TARGET} voittoa)"
    return None


def _render(error: str | None = None):
    game = _current_game()
    status = _status_text(game["tuomari"])
    finished = _has_winner(game["tuomari"])
    winner = _winner_text(game["tuomari"])
    return render_template_string(
        TEMPLATE,
        game=game,
        status=status,
        finished=finished,
        winner=winner,
        error=error,
        mode_labels=MODE_LABELS,
        win_target=WIN_TARGET,
    )


@app.route("/", methods=["GET"])
def home():
    return _render()


@app.route("/start", methods=["POST"])
def start():
    mode = request.form.get("mode")
    if mode not in MODE_LABELS:
        return _render("Valitse pelimuoto.")
    _reset_game(mode)
    return redirect(url_for("home"))


@app.route("/move", methods=["POST"])
def move():
    game = _current_game()
    if not game.get("mode"):
        return _render("Valitse pelimuoto ensin.")

    if _has_winner(game["tuomari"]):
        return _render("Peli on jo päättynyt. Aloita uusi peli.")

    first = request.form.get("first_move", "").strip().lower()
    if first not in VALID_MOVES:
        return _render("Sallitut siirrot ovat k, p ja s.")

    second = None
    if game["mode"] == "pvp":
        second = request.form.get("second_move", "").strip().lower()
        if second not in VALID_MOVES:
            return _render("Toisen pelaajan siirto puuttuu tai on virheellinen.")
    else:
        ai = game["ai"]
        second = ai.anna_siirto()
        ai.aseta_siirto(first)

    game["tuomari"].kirjaa_siirto(first, second)
    game["history"].append({
        "first": first,
        "second": second,
        "score": _status_text(game["tuomari"]),
    })

    return redirect(url_for("home"))


@app.route("/reset", methods=["POST"])
def reset():
    game = _current_game()
    if game.get("mode"):
        _reset_game(game["mode"])
    return redirect(url_for("home"))


TEMPLATE = """
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Kivi-Paperi-Sakset</title>
    <style>
        :root {
            --bg: #f0f4f8;
            --panel: #ffffff;
            --accent: #1f7a8c;
            --accent-2: #022b3a;
            --text: #0b1724;
            --muted: #5a6b7b;
            --border: #d7e0e7;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: "IBM Plex Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
            background: radial-gradient(circle at 20% 20%, rgba(31, 122, 140, 0.1), transparent 35%),
                        radial-gradient(circle at 80% 0%, rgba(2, 43, 58, 0.1), transparent 28%),
                        var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        .shell {
            max-width: 960px;
            margin: 0 auto;
            padding: 32px 16px 48px;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }
        h1 { margin: 0; letter-spacing: -0.5px; }
        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            box-shadow: 0 14px 40px rgba(2, 43, 58, 0.08);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 18px;
        }
        .row { display: flex; flex-wrap: wrap; gap: 14px; }
        .col { flex: 1; min-width: 260px; }
        form { margin: 0; }
        label { display: block; font-weight: 600; margin-bottom: 6px; }
        select, input[type="text"] {
            width: 100%;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: #f8fbfd;
            font-size: 15px;
        }
        input[type="text"] { text-transform: lowercase; }
        .actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
        button {
            padding: 10px 14px;
            border-radius: 10px;
            border: none;
            background: var(--accent);
            color: #fff;
            font-weight: 700;
            cursor: pointer;
            letter-spacing: 0.2px;
        }
        button.secondary { background: var(--accent-2); }
        button.ghost { background: transparent; color: var(--accent-2); border: 1px solid var(--border); }
        .muted { color: var(--muted); font-size: 14px; }
        .status { font-weight: 700; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px 6px; text-align: left; border-bottom: 1px solid var(--border); }
        th { font-size: 14px; text-transform: uppercase; letter-spacing: 0.4px; color: var(--muted); }
        .error { color: #b00020; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="shell">
        <header>
            <div>
                <h1>Kivi-Paperi-Sakset</h1>
                <div class="muted">Valitse pelimuoto ja syötä siirrot (k, p tai s).</div>
            </div>
            <form action="/reset" method="post">
                <button class="ghost" type="submit">Tyhjennä peli</button>
            </form>
        </header>

        <section class="card">
            <form action="/start" method="post" class="row">
                <div class="col">
                    <label>Pelimuoto</label>
                    <select name="mode" onchange="this.form.submit()">
                        <option value="">Valitse...</option>
                        {% for key, label in mode_labels.items() %}
                            <option value="{{ key }}" {% if game.mode == key %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col" style="align-self: flex-end;">
                    <div class="muted">Nykyinen: {{ mode_labels.get(game.mode, 'ei valintaa') }}</div>
                    <div class="muted">Peli päättyy kun jompikumpi saavuttaa {{ win_target }} voittoa.</div>
                </div>
            </form>
        </section>

        <section class="card">
            <form action="/move" method="post">
                {% if error %}<div class="error">{{ error }}</div>{% endif %}
                <div class="row">
                    <div class="col">
                        <label>Ensimmäisen pelaajan siirto</label>
                        <input name="first_move" maxlength="1" placeholder="k / p / s" autocomplete="off" {% if finished %}disabled{% endif %} />
                    </div>
                    {% if game.mode == 'pvp' %}
                    <div class="col">
                        <label>Toisen pelaajan siirto</label>
                        <input name="second_move" maxlength="1" placeholder="k / p / s" autocomplete="off" {% if finished %}disabled{% endif %} />
                    </div>
                    {% else %}
                    <div class="col">
                        <label>Toinen pelaaja</label>
                        <div class="muted">Tietokone valitsee automaattisesti.</div>
                    </div>
                    {% endif %}
                </div>
                <div class="actions" style="margin-top: 12px;">
                    <button type="submit" {% if finished %}disabled{% endif %}>Kirjaa siirrot</button>
                    <div class="muted">Peli päättyy virheelliseen syötteeseen (k/p/s).</div>
                </div>
            </form>
        </section>

        <section class="card">
            <div class="status">{{ status | safe }}</div>
            {% if winner %}
            <div class="muted">{{ winner }}</div>
            {% endif %}
        </section>

        <section class="card">
            <h3>Historia</h3>
            {% if game.history %}
            <table>
                <thead>
                    <tr><th>#</th><th>Ensimmäinen</th><th>Toinen</th><th>Tila</th></tr>
                </thead>
                <tbody>
                    {% for row in game.history %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ row.first }}</td>
                        <td>{{ row.second }}</td>
                        <td>{{ row.score | safe }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="muted">Ei pelattuja kierroksia.</div>
            {% endif %}
        </section>
    </div>
</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)
