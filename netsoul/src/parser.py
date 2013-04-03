###
###
###
###
###
###

import  sys

class   command:

    def __init__(self, function, minarg, command):
        self.function = function
        self.minarg = minarg
        self.command = command

class   parser:

    def __init__(self, hooks, obj):
        self.hooks = hooks
        self.obj = obj

    def parse(self):
        if (len(sys.argv) == 1):
            text = ''
        else:
            text = sys.argv[1]
        for hook in self.hooks:
            if (len(sys.argv) >= hook.minarg) and hook.command == text:
                print 'Found : %s' % hook.command
                hook.function(self.obj)
        print 'Nothing found...'
