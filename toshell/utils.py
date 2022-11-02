class ExitMixin():

    def do_exit(self, _):
        '''
        Exit the shell.
        '''
        print(self._exit_msg)
        return True

    def do_EOF(self, params):
        print()
        return self.do_exit(params)

def dict_rev_lookup(dict, value):
    return list(dict.keys())[list(dict.values()).index(value)]
