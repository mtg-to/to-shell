'''
Created on 15 Mar 2021

@author: piotr
'''
from cmd import Cmd
from toshell.utils import ExitMixin
import csv

class PlayersShell(Cmd, ExitMixin):

    prompt="PLAYERS> "
    _exit_msg=""

    def __init__(self, state, ck='tab', stdin=None, stdout=None):
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)
        self._state = state

    def do_load(self, path):
        players = {}
        try:
            with open(path, "r") as players_file:
                for line in csv.reader(players_file):
                    players[line[0]] = line[1]
            self._state.players = players
            return True
        except Exception as ex:
            print(f"Couldn't load: {ex}")

    def do_save(self, path):
        try:
            with open(path, "w") as players_file:
                writer = csv.writer(players_file)
                for (plid, name) in self._state.players.items():
                    writer.writerow([plid, name])
        except Exception as ex:
            print(f"Couldn't save: {ex}")

    def do_list(self, _):
        for (plid, name) in self._state.players.items():
            print(f"{plid}: {name}")

    def do_remove(self, plid):
        if plid in self._state.players:
            del self._state.players[plid]

    def do_add(self, player_def):
        (plid, name) = player_def.split(":")
        if not plid or not name:
            self.do_help_add()
            return
        self._state.players[plid] = name