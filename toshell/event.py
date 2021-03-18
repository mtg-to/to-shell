'''
Created on 18 May 2020

@author: Piotr Berlowski
'''

from cmd import Cmd

import toshell.labels
import pypair

from toshell.utils import ExitMixin
from pypair import Tournament

POINTS_KEY = "Points"
OMW_KEY = "OMW%"
NAME_KEY = "Name"

pypair.debuglevel = 2

class EventManageShell(Cmd, ExitMixin):

    prompt = 'MANAGE> '
    _exit_msg = toshell.labels.EVENT_OUTRO_TEXT 

    def _init_event(self, state, evid):
        if not evid in state.events:
            state.events[evid] = Tournament()
            self.intro = toshell.labels.EVENT_INTRO_NEW_TEXT
        else:
            self.intro = toshell.labels.EVENT_INTRO_TEXT

    def __init__(self, state, evid, ck='tab', stdin=None, stdout=None):
        self.prompt = f"Event {evid}> "
        self._init_event(state, evid)
        self._evid = evid
        self._event = state.events[evid]
        self._players = state.players
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)

    def do_list_players(self, _):
        for (plid, nick) in self._players.items():
            print(f"{plid}: {nick}")

    def _enroll_one(self, plid):
        if plid in self._players:
            nick = self._players[plid]
            self._event.addPlayer(plid, nick)
            print(f"{nick} enrolled.")
        else: 
            print(f"No player with ID {plid}")

    def do_enroll(self, plid):
        if 'all' == plid:
            self.do_enroll_all(plid)
        else:
            self._enroll_one(plid)

    def do_enroll_all(self, _):                     
        for plid in self._players.keys():
            self._enroll_one(plid)

    def do_standings(self, _):
        standings = sorted(self._event.playersDict.values(), key=lambda p: p[POINTS_KEY]+float(p[OMW_KEY]), reverse=True)
        col_width = max(len(p[NAME_KEY]) for p in standings) + 2
        print(f"PLACE:\t{'PLAYER'.ljust(col_width)}\tPOINTS\tOMW%")
        for place, player in enumerate(standings):
            print(f"{place+1}:\t{player[NAME_KEY].ljust(col_width)}\t{player[POINTS_KEY]}\t{player[OMW_KEY]}")

    def do_pair(self, _):
        if self._event.playersDict:
            self._event.pairRound()
            RoundShell(self._evid, self._event, self._players, self.completekey, self.stdin, self.stdout).cmdloop()
        else:
            print("No players enrolled!")

    def do_bye(self, plid):
        if str(plid) in self._players.keys():
            self._event.assignBye(str(plid))
        else:
            print("No player with that id!")

    def do_match(self, plids):
        plids = plids.split()
        self._event.pairPlayers(str(plids[0]), str(plids[1]))


class RoundShell(Cmd):

    _exit_msg = "Round finished!"

    def __init__(self, evid, event, players, ck='tab', stdin=None, stdout=None):
        self._event = event
        self._players = players
        self._round = event.currentRound
        self.prompt = f"{evid} round {self._round}> "
        self.intro = f"Starting round {self._round}!"
        self._results = {}
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)
        self.do_pairings()

    def do_pairings(self, _=None):
        for (table, pair) in self._event.roundPairings.items():
            print(f"Table {table} - {self._players[pair[0]]} : {self._players[pair[1]]}")
            if table in self._results:
                print(f"Result: {' - '.join(str(r) for r in self._results[table])}")
            else:
                print("Still playing!")

    def do_report(self, params):
        tables = self._event.roundPairings
        args = params.split(" ")
        if len(args) == 1:
            self._query_result(params)
        else:
            tbl = int(args[0])
            if tbl and tbl in tables:
                res = args[1].split("-")
                if len(res) < 2:
                    print(f"Invalid result: {res}!")
                else:
                    print(f"Table {tbl}: {args[1]}")
                    self._results[tbl] = [int(r) for r in res]

    def _query_result(self, table_str):
        tables = self._event.roundPairings
        table = int(table_str)
        if table and table in tables:
            pair = tables[table]
            p1 = int(input(f"{self._players[pair[0]]} wins: "))
            p2 = int(input(f"{self._players[pair[1]]} wins: "))
            d = int(input("Draws: "))
            print(f"Table {table}: {p1}-{p2}-{d}")
            self._results[table] = [p1, p2, d]
        else:
            print(f"Table '{table}' does not exist!")

    def do_submit(self, _):
        missing = set(self._event.tablesOut) - set(self._results.keys())
        if missing:
            print(f"Missing results for tables: {missing}")
        else:
            results = dict(self._results)
            for table, res in self._results.items():
                if len(res) < 3: res += [0]*(3 - len(res))
                self._event.reportMatch(table, res)
                del results[table]
            self._results = results
            if not results: 
                return True
