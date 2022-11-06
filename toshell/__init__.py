from cmd import Cmd

import sys

import toshell.labels
from toshell.models import ShellState
from toshell.utils import ExitMixin
from toshell.players import PlayersShell
from toshell.labels import SHELL_INTRO_TEXT, SHELL_OUTRO_TEXT
from toshell.event import EventManageShell
from toshell.game.mtg import MtgResultFactory
from toshell.game.fow import FoWResultFactory
from toshell.memento.recorder import recorder
from toshell.memento.recorder import TypeCapture

class TOShell(Cmd, ExitMixin):

    prompt = "TO> "
    intro = SHELL_INTRO_TEXT
    _exit_msg = SHELL_OUTRO_TEXT

    @recorder.record_init(assign="to")
    def __init__(self, ck="tab", stdin=None, stdout=None):
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)
        self._state = ShellState()

    def do_list_events(self, _):
        for evid in self._state.events.keys():
            print(evid)

    def do_manage(self, evid):
        if not evid:
            self.help_manage()
        else:
            self.api_manage(evid).cmdloop()

    @recorder.record_command(
        assign="evt", captures=[TypeCapture("result_factory_factory")]
    )
    def api_manage(self, evid, result_factory_factory=MtgResultFactory):
        return EventManageShell(
            self._state,
            evid,
            result_factory_factory(),
            self.completekey,
            self.stdin,
            self.stdout,
        )

    def help_manage(self):
        print(toshell.labels.EVENT_MANAGE_HELP)

    def do_fow(self, evid):
        if not evid:
            self.help_manage()
        else:
            self.api_manage(evid, result_factory_factory=FoWResultFactory).cmdloop()

    def help_fow(self):
        print(toshell.labels.EVENT_MANAGE_HELP)

    @recorder.record_command(assign="players")
    def api_players(self):
        return PlayersShell(self._state, self.completekey, self.stdin, self.stdout)

    def do_players(self, params):
        pshell = self.api_players()
        if params:
            pshell.do_load(params)
        else:
            pshell.cmdloop()

    def help_players(self):
        print(toshell.labels.PLAYERS_MANAGE_HELP)

def main():
    recorder.start()
    recorder.register_import(TOShell)
    recorder.register_import(FoWResultFactory)
    recorder.register_import(MtgResultFactory)
    TOShell().cmdloop()

