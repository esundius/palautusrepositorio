from flask import session
from web_app import app


def test_home_page_loads():
    with app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Kivi-Paperi-Sakset" in resp.get_data(as_text=True)


def test_start_and_move_with_ai_mode():
    with app.test_client() as client:
        resp = client.post("/start", data={"mode": "ai"}, follow_redirects=True)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "Nykyinen" in html

        resp = client.post("/move", data={"first_move": "k"}, follow_redirects=True)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "Pelitilanne" in html
        assert any(mark in html for mark in ["0 - 1", "1 - 0", "0 - 0"])


def test_game_ends_at_three_wins_and_blocks_extra_moves():
    with app.test_client() as client:
        client.post("/start", data={"mode": "pvp"}, follow_redirects=True)

        for _ in range(3):
            resp = client.post(
                "/move",
                data={"first_move": "k", "second_move": "s"},
                follow_redirects=True,
            )
            assert resp.status_code == 200

        html = resp.get_data(as_text=True)
        assert "3 - 0" in html
        assert "voitti" in html

        resp = client.post(
            "/move",
            data={"first_move": "k", "second_move": "s"},
            follow_redirects=True,
        )
        html = resp.get_data(as_text=True)
        assert "Peli on jo päättynyt" in html
        assert "4 - 0" not in html


def test_invalid_first_move_shows_error():
    with app.test_client() as client:
        client.post("/start", data={"mode": "ai"}, follow_redirects=True)
        resp = client.post("/move", data={"first_move": "x"}, follow_redirects=True)
        assert resp.status_code == 200
        assert "Sallitut siirrot" in resp.get_data(as_text=True)


def test_pvp_requires_second_move():
    with app.test_client() as client:
        client.post("/start", data={"mode": "pvp"}, follow_redirects=True)
        resp = client.post("/move", data={"first_move": "k", "second_move": ""}, follow_redirects=True)
        assert resp.status_code == 200
        assert "Toisen pelaajan siirto puuttuu" in resp.get_data(as_text=True)
