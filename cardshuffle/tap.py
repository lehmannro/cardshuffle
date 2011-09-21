# Copyright (C) 2010 Robert Lehmann

import cardshuffle
from cardshuffle.server import Lobby
from twisted.python import usage
from twisted.application import strports

class Options(usage.Options):
    synopsis = "[options] [port]"
    longdesc = ("Starts a CardShuffle server imposing the defined ruleset."
               " [default port: 1030]")
    optParameters = [
        ["players", "", 3,
            "players required for a game", int],
        ["deck", "", 10,
            "minimum amount of cards in a deck", int],
        ["decklimit", "", 0,
            "maximum amount of cards in a deck (0 for unlimited)", int],
        ["hand", "", 6,
            "inventory a player can carry at any time", int],
        ["mana", "", 200,
            "mana a player cannot exceed by default", int],
        ["health", "", 200,
            "health points a player cannot exceed by default", int],
        #XXX draws - draw points a player cannot exceed by periodic draw gains
        ["regenerate", "", 5,
            "seconds until a health point recharges", float],
        ["replenish", "", 0.9,
            "seconds until a mana point replenishes", float],
        ["drawgain", "", 30,
            "seconds until players gain another draw point", float],
        ["initial-draws", "", -1,
            "draw points players start with (-1 for hand size)", int],
    ]
    def parseArgs(self, port="1030"):
        self['port'] = port
    def postOptions(self):
        if self['initial-draws'] == -1:
            self['initial-draws'] = self['hand']
    def opt_version(self):
        print "Cardshuffle version:", cardshuffle.__version__
        return usage.Options.opt_version(self)


def makeService(config):
    t = Lobby(config)
    return strports.service(config['port'], t)
