from cmd import Cmd


import toshell.labels
from toshell.models import ShellState
from toshell.utils import ExitMixin
from toshell.players import PlayersShell
from toshell.labels import SHELL_INTRO_TEXT, SHELL_OUTRO_TEXT
from toshell.event import EventManageShell


class TOShell(Cmd, ExitMixin):
    
    prompt = 'TO> '
    intro = SHELL_INTRO_TEXT
    _exit_msg = SHELL_OUTRO_TEXT
    
    def __init__(self, ck='tab', stdin=None, stdout=None):
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)
        self._state = ShellState()
    
    def do_list_events(self, _):
        for evid in self._state.events.keys():
            print(evid)

    def do_manage(self, evid):
        if not evid:
            self.help_manage()
        else:
            EventManageShell(self._state, evid, self.completekey, self.stdin, self.stdout).cmdloop()

    def help_manage(self):
        print(toshell.labels.EVENT_MANAGE_HELP)

    def do_players(self, params):
        pshell = PlayersShell(self._state, self.completekey, self.stdin, self.stdout)
        if params:
            pshell.do_load(params)
        else:
            pshell.cmdloop()

def main():
    TOShell().cmdloop()
