class ShellState:

    def __init__(self):
        self._events=dict()
        self._players=dict()

    @property
    def events(self):
        return self._events

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, val):
        self._players = val
