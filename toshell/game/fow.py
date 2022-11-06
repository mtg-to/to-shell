from abc import ABC
from dataclasses import dataclass
from pypair import (
    BasicRoundResult,
    ResultType,
    WLDPointsCalculator,
    omw_tb,
    PlayerRecord,
    ByeResult,
)
from functools import cmp_to_key
from toshell.game.api import (
    MatchResult,
    ResultFactory,
)


def bfp_tb(player: PlayerRecord):
    return sum((res.bf_points for res in player.results if not isinstance(res, ByeResult)))

@dataclass
class FoWRoundResult(BasicRoundResult):
    bf_points: int


class FoWMatchResult(MatchResult):
    def __init__(self, p1, p1bf, p2, p2bf):
        if p1bf >= p2bf:
            self._set_res(p1, p1bf, p2, p2bf)
        else:
            self._set_res(p2, p2bf, p1, p1bf)

    def _set_res(self, winner, wbf, looser, lbf):
        self.winner = winner
        self.wbf = int(wbf)
        self.looser = looser
        self.lbf = int(lbf)

    def _is_win(self):
        return self.wbf > 3

    def technical(self):
        return {
            self.winner: FoWRoundResult(
                opponent=self.looser,
                result=ResultType.WIN if self._is_win() else ResultType.DRAW,
                bf_points=self.wbf,
            ),
            self.looser: FoWRoundResult(
                opponent=self.winner,
                result=ResultType.LOSS if self._is_win() else ResultType.DRAW,
                bf_points=self.lbf,
            ),
        }

    def descriptive(self, players):
        if self._is_win():
            return f"{players[self.winner.id]} wins {self.wbf}-{self.lbf}"
        return f"Both players lost {players[self.winner.id]}:{self.wbf} - {players[self.looser.id]}:{self.lbf}"


class FoWResultFactory(ResultFactory):
    def points_calculator(self):
        return WLDPointsCalculator(
            values={
                ResultType.WIN: 1,
                ResultType.DRAW: 0,
                ResultType.LOSS: 0,
            },
            tiebreak_calcs=[
                bfp_tb,
                omw_tb,
            ],
        )

    def interpret(self, table, res_string):
        results = res_string.split("-")
        if len(results) < 2 or len(results) > 3:
            print(
                f"Result must be reported as '[Player 1 bf points]-[Player 2 bf points]' - got: {res_string}"
            )
            return None
        try:
            i_r0=int(results[0])
            i_r1=int(results[1])
        except ValueError:
            print(
                f"Result must be reported as '[Player 1 bf points]-[Player 2 bf points]' - got: {res_string}"
            )
            return None
        return FoWMatchResult(table[0], i_r0, table[1], i_r1)

    def query_result(self, p1, p2):
        p1score = input(f"{p1} BF Points: ")
        p2score = input(f"{p2} BF Points: ")
        return f"{p1score}-{p2score}"

def input_int(msg):
    val = None
    while not val:
        try:
            val = int(input(msg))
        except (ValueError, TypeError):
            print("Please enter a valid nuber!")
    return val