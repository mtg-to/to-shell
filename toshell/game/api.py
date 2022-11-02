from abc import ABC
from abc import abstractmethod
from pypair import WLDPointsCalculator

class MatchResult(ABC):

    @abstractmethod
    def technical(self):
        pass

    @abstractmethod
    def descriptive(self, players):
        pass

class ResultFactory(ABC):

    def points_calculator(self):
        return WLDPointsCalculator()

    @abstractmethod
    def interpret(self, table, res_string):
        pass

    @abstractmethod
    def query_result(self, table, players):
        pass