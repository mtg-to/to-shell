'''
Created on 16 May 2020

@author: Piotr Berlowski
'''

SHELL_INTRO_TEXT='''
Welcome to Tournament Organizer Shell.

* Type "?" to list available commands.
* Type "help <command>" to learn more about the command.
* Type "exit" to finish the session.
'''

SHELL_OUTRO_TEXT='''
Thanks for using the Tournament Organizer Shell!
'''

EVENT_INTRO_TEXT='''
Event opened, type 'exit' to finish.
'''

EVENT_INTRO_NEW_TEXT='''
Event created, type 'exit' to finish.
'''

EVENT_OUTRO_TEXT='''
Leaving event.
'''


EVENT_HELP_LIST='''
Lists created events.
'''

EVENT_EXISTS_ERROR='''
Event with this ID already exists! Did you mean `manage`?
'''

EVENT_DOES_NOT_EXIST_ERROR='''
Event with this ID does not exist! Did you mean `create`?
'''

EVENT_HELP='''
Usage: event

Use this command to manage events.
'''

EVENT_CREATE_HELP='''
Usage: create {evid}
  * evid - event identifier

Creates an event named {evid}.
'''

EVENT_MANAGE_HELP='''
Usage: managee {evid}
  * evid - event identifier

Opens a management console for an event named {evid}.
'''
