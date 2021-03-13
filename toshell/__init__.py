from cmd import Cmd
from toshell.labels import INTRO_TEXT
from toshell.event import EventManagerCommand

class TOShell(Cmd):
    
    prompt = 'TO> '
    intro = INTRO_TEXT
    
    def __init__(self, ck='tab', stdin=None, stdout=None):
        super().__init__(completekey=ck, stdin=stdin, stdout=stdout)
        self.event = EventManagerCommand()
    
    def do_event(self, params):
        self.event.execute(params)
        
    def help_event(self):
        self.event.help()
    
    def do_exit(self, params):
        '''
        Exit the shell.
        '''
        print('Thanks for using TO Shell!')
        return True

    def do_EOF(self, params):
        print()
        return self.do_exit(params)

def main():
    TOShell().cmdloop()