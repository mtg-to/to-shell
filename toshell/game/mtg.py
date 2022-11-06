from pypair import BasicRoundResult, ResultType, WLDPointsCalculator
from functools import cmp_to_key
from toshell.game.api import ResultFactory
from toshell.game.api import MatchResult


class MtgMatchResult(MatchResult):
    def __init__(self, p1, p1score, p2, p2score):
        if p1score == p2score:
            self._technical = self._make_draw(p1, p2)
            self._descriptive = lambda players: "DRAW"
        elif p1score > p2score:
            self._technical = self._make_win(p1, p2)
            self._descriptive = lambda players: f"{players[p1.id]} WIN"
        else:
            self._technical = self._make_win(p2, p1)
            self._descriptive = lambda players: f"{players[p2.id]} WIN"

    def _make_draw(self, p1, p2):
        return {
            p1: BasicRoundResult(p2, ResultType.DRAW),
            p2: BasicRoundResult(p1, ResultType.DRAW),
        }

    def _make_win(self, winner, looser):
        return {
            winner: BasicRoundResult(looser, ResultType.WIN),
            looser: BasicRoundResult(winner, ResultType.LOSS),
        }

    def technical(self):
        return self._technical

    def descriptive(self, players):
        return self._descriptive(players)


class MtgResultFactory(ResultFactory):
    def points_calculator(self):
        return WLDPointsCalculator()

    def interpret(self, table, res_string):
        results = res_string.split("-")
        if len(results) < 2 or len(results) > 3:
            print(
                f"Result must be reported as '[wins p1]-[wins p2](-[draws]) - got: {res_string}"
            )
            return None
        return MtgMatchResult(table[0], results[0], table[1], results[1])

    def query_result(self, p1, p2):
        p1score = input(f"{p1} wins: ")
        p2score = input(f"{p2} wins: ")
        d = input("Draws: ")
        return f"{p1score}-{p2score}-{d}"
