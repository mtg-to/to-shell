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
Usage: manage {evid}
  * evid - event identifier

Opens a management console for an event named {evid}.
'''

EVENT_MATCH_HELP='''
Usage: match {plid1},{plid2}
  * plid1 - id of player 1
  * plid2 - id of player 2

Forces a pairing of player 1 with player 2.
'''


PLAYERS_MANAGE_HELP='''
Usage: players ({path})
  * path (optional) - path to the player database to open

Opens a player database management console (optionally loading the specified CSV).
'''

PLAYER_ADD_HELP='''
Usage: add {plid:name}
  * plid - player identifier
  * name - player name

Adds player to the player database.
'''

PLAYER_LIST_SAVE_HELP='''
Usage: save {path}
  * path - path to where the player list is to be saved

Saves the player database to a CSV file.
'''