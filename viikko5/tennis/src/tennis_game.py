class TennisGame:
    SCORE_NAMES = {0: "Love", 1: "Fifteen", 2: "Thirty", 3: "Forty"}

    def __init__(self, player1_name, player2_name):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.score1 = 0
        self.score2 = 0

    def won_point(self, player_name):
        # Accept either the literal test names "player1"/"player2"
        # or the actual player name strings provided at construction.
        if player_name == "player1" or player_name == self.player1_name:
            self.score1 += 1
        elif player_name == "player2" or player_name == self.player2_name:
            self.score2 += 1
        else:
            raise ValueError(f"Unknown player: {player_name}")

    def _tie_score(self):
        if self.score1 < 3:
            return f"{self.SCORE_NAMES[self.score1]}-All"
        return "Deuce"

    def _advantage_or_win(self):
        diff = self.score1 - self.score2
        if diff == 1:
            return "Advantage player1"
        if diff == -1:
            return "Advantage player2"
        if diff >= 2:
            return "Win for player1"
        return "Win for player2"

    def _normal_score(self):
        left = self.SCORE_NAMES.get(self.score1, str(self.score1))
        right = self.SCORE_NAMES.get(self.score2, str(self.score2))
        return f"{left}-{right}"

    def get_score(self):
        if self.score1 == self.score2:
            return self._tie_score()

        if self.score1 >= 4 or self.score2 >= 4:
            return self._advantage_or_win()

        return self._normal_score()
