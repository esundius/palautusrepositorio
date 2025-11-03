import unittest
from statistics_service import StatisticsService
from player import Player

class PlayerReaderStub:
    def get_players(self):
        return [
            Player("Semenko", "EDM", 4, 12),  #  4+12 = 16
            Player("Lemieux", "PIT", 45, 54), # 45+54 = 99
            Player("Kurri",   "EDM", 37, 53), # 37+53 = 90
            Player("Yzerman", "DET", 42, 56), # 42+56 = 98
            Player("Gretzky", "EDM", 35, 89)  # 35+89 = 124
        ]

class TestStatisticsService(unittest.TestCase):
    def setUp(self):
        # annetaan StatisticsService-luokan oliolle "stub"-luokan olio
        self.stats = StatisticsService(
            PlayerReaderStub()
        )

    def test_search_finds_player(self):
        player = Player("Kurri",   "EDM", 37, 53)
        self.assertEqual(str(self.stats.search("Kurri")), str(player))
    
    def test_search_does_not_find_unknown_player(self):
        self.assertIsNone(self.stats.search("Mats"))
    
    def test_team_returns_correct_list(self):
        self.assertEqual(self.stats.team("PIT")[0].name, "Lemieux")

    def test_top_player(self):
        self.assertEqual(self.stats.top(1)[0].name, "Gretzky")
