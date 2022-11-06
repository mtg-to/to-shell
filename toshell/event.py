'''
Created on 18 May 2020

@author: Piotr Berlowski
'''

from cmd import Cmd

import toshell.labels
import pypair

from toshell.utils import ExitMixin
from toshell.utils import dict_rev_lookup
from toshell.game.mtg import MtgResultFactory
from toshell.memento.recorder import recorder
from functools import cmp_to_key
from toshell.labels import EVENT_MATCH_HELP

POINTS_KEY = "Points"
OMW_KEY = "OMW%"
NAME_KEY = "Name"

pypair.debuglevel = 1

class EventManageShell(Cmd, ExitMixin):

    prompt = 'MANAGE> '
    _exit_msg = toshell.labels.EVENT_OUTRO_TEXT 

    def _init_event(self, state, evid):
        if not evid in state.events:
            state.events[evid] = pypair.Tournament(calculator=self._result_factory.points_calculator())
            self.intro = toshell.labels.EVENT_INTRO_NEW_TEXT
        else:
            self.intro = toshell.labels.EVENT_INTRO_TEXT

    def __init__(self, state, evid, result_factory, ck='tab', stdin=None, stdout=None):
        self.prompt = f"Event {evid}> "
        self._result_factory = result_factory
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

    @recorder.record_command()
    def do_enroll(self, plid):
        if 'all' == plid:
            self.do_enroll_all(plid)
        else:
            self._enroll_one(plid)

    @recorder.record_command()
    def do_enroll_all(self, _):
        for plid in self._players.keys():
            self._enroll_one(plid)

    def do_bye(self, plid):
        if plid in self._players.keys():
            self._event.assign_bye_by_id(plid)
            print(f"{self._players[plid]} gets a bye!")
        else:
            print(f"No player with ID {plid}")

    def do_match(self, plids):
        a_plid = [plid.strip() for plid in plids.split(",")]
        if len(a_plid) == 2\
            and a_plid[0] in self._players\
            and a_plid[1] in self._players:
            self._event.pair_players_by_id(*a_plid)
        else:
            print(f"Could not pair {a_plid}!")

    def help_match(self):
        print(HELP)

    def do_standings(self, _):
        calc = self._result_factory.points_calculator()
        standings = sorted(self._event.playersDict.values(), key=cmp_to_key(calc.standings_comparator), reverse=False)
        col_width = max(len(p) for p in self._players.values()) + 2
        header = f"PLACE:\t{'PLAYER'.ljust(col_width)}\tPOINTS"
        for i,_ in enumerate(calc.tiebreak_calcs):
            header += f"\tTB{i}"
        print(header)
        for place, player in enumerate(standings):
            pname = self._players[player.id]
            plid = player.id
            _display_name=f"{plid}:{pname}"
            tiebreaks = "\t".join((str(tb) for tb in player.tiebreaks))
            print(f"{place+1}:\t{_display_name.ljust(col_width)}\t{player.points_total(calc)}\t{tiebreaks}")

    @recorder.record_command(assign="rnd")
    def api_pair(self):
        if self._event.playersDict:
            self._event.pairRound(forcePair=True)
            self._spoof_pairing_recording()
            return RoundShell(self._evid, self._event, self._players, self._result_factory, self.completekey, self.stdin, self.stdout)
        else:
            print("No players enrolled!")
            return None

    def _spoof_pairing_recording(self):
        do_match = recorder.spoof_command("do_match")
        for (table, pair) in self._event.roundPairings.items():
            pairstr=",".join((p.id for p in pair))
            do_match(self, pairstr)

    def do_pair(self, _):
        if api := self.api_pair():
            api.cmdloop()

class RoundShell(Cmd):

    _exit_msg = "Round finished!"

    def __init__(self, evid, event, players, result_factory, ck='tab', stdin=None, stdout=None):
        self._event = event
        self._players = players
        self._round = event.currentRound
        self.prompt = f"{evid} round {self._round}> "
        self.intro = f"Starting round {self._round}!"
        self._results = {}
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)
        self.do_pairings()
        self._result_factory = result_factory

    def do_pairings(self, _=None):
        for (table, pair) in self._event.roundPairings.items():
            p1id, p2id = (p.id for p in pair)
            print(f"Table {table} - {p1id}:{self._players[p1id]} vs. {p2id}:{self._players[p2id]}")
            if table in self._results:
                print(self._results[table].descriptive(self._players))
            else:
                print("Still playing!")

    def do_report(self, params):
        print(f"got params: {params} ({len(params)})")
        if not params:
            print(f"Table needed!")
            return
        args = params.split(" ")
        tblid = int(args[0])
        tables = self._event.roundPairings
        if not tblid or tblid not in tables:
            print(f"Table {tblid} not found!")
            return
        if len(args) == 1:
            points = self._result_factory.query_result(self._players[tables[tblid][0].id],self._players[tables[tblid][1].id])
        else:
            points = args[1]
        self.api_report(tblid, points)


    @recorder.record_command()
    def api_report(self, tblid, points_str):
        tblid = int(tblid)
        tables = self._event.roundPairings
        table = tables[tblid]
        result = self._result_factory.interpret(table, points_str)
        if result:
            self._results[tblid] = result

    @recorder.record_command()
    def do_submit(self, _):
        missing = set(self._event.tablesOut) - set(self._results.keys())
        if missing:
            print(f"Missing results for tables: {missing}")
        else:
            results = dict(self._results)
            for table, res in self._results.items():
                self._event.reportMatch(table, res.technical())
                del results[table]
            self._results = results
            if not results: 
                return True
