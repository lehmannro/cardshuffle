# Copyright (C) 2010 Robert Lehmann

from cardshuffle.server import Lobby
from twisted.python import usage
from twisted.application import strports

class Options(usage.Options):
    synopsis = "[-n players] [port]"
    longdesc = "Makes a CardShuffle server."
    optParameters = [
        ["number", "n", 3, "amount of players required for a game", int],
    ]
    def parseArgs(self, port="1030"):
        self['port'] = port

def makeService(config):
    t = Lobby(config['number'])
    return strports.service(config['port'], t)
