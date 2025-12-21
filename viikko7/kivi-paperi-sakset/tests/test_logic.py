from tuomari import Tuomari
from tekoaly import Tekoaly
from tekoaly_parannettu import TekoalyParannettu


def test_tuomari_scores_wins_and_ties():
    t = Tuomari()
    t.kirjaa_siirto("k", "s")  # first wins
    t.kirjaa_siirto("p", "s")  # second wins
    t.kirjaa_siirto("s", "s")  # tie
    assert t.ekan_pisteet == 1
    assert t.tokan_pisteet == 1
    assert t.tasapelit == 1


def test_tekoaly_cycles_moves():
    ai = Tekoaly()
    assert ai.anna_siirto() == "p"
    assert ai.anna_siirto() == "s"
    assert ai.anna_siirto() == "k"
    assert ai.anna_siirto() == "p"


def test_tekoaly_parannettu_prefers_counter_move():
    ai = TekoalyParannettu(3)
    ai.aseta_siirto("k")
    ai.aseta_siirto("k")
    ai.aseta_siirto("k")
    # Most frequent observed move is k -> should return paper to beat it
    assert ai.anna_siirto() == "p"
