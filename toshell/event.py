import argparse

'''
Created on 18 May 2020

@author: Piotr Berlowski
'''

class Command(object):
    
    def __init__(self, name, description, registration_callback):
        parser = argparse.ArgumentParser(prog=name, description=description, add_help=False)
        subparsers = parser.add_subparsers(dest='subcommand', required=True)
        registration_callback(subparsers)
        self.parser = parser

    def help(self):
        self.parser.print_help()
        
    def execute(self, line):
        try: 
            args = self.parser.parse_args(line.split())
            args.action(args)
        except SystemExit:
            self.parser.print_help()
            


class EventManagerCommand(Command):

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('event', 'event management utility', self._register)
        
    def _register(self, subparsers):
        create_parser = subparsers.add_parser('create', help='Create a new event')
        create_parser.add_argument('name', help='Name of the event to create')
        create_parser.set_defaults(action=self._create_event)

    def _create_event(self, args):
        print('Creating event "%s"' % args.name)
