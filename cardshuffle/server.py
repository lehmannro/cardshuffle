# encoding: utf-8
# Copyright (C) 2010 Robert Lehmann

from cardshuffle.player import Player
from cardshuffle.client import Shuffle
from cardshuffle.game import Session

from twisted.internet import protocol, task

import operator

TICKINTERVAL = 0.02 # 50 fps

class MulticastServerFactory(protocol.ServerFactory):
    """Enables pooling of clients and broadcasting among them.

    Connected sessions are stored in :ivar:`connections`.

    """
    def startFactory(self):
        self.connections = []

    def buildProtocol(self, addr):
        """Add connection to pool."""
        proto = protocol.ServerFactory.buildProtocol(self, addr)
        self.connections.append(proto)
        return proto

    def clientConnectionLost(self, proto, reason):
        """Remove connection from pool."""
        protocol.ServerFactory.clientConnectionLost(self, proto, reason)
        self.connections.pop(proto)

    def broadcast(self, message):
        """Send a message to all connected clients. This may include
        connections which are not part of a particular group or session.

        """
        for connection in self.connections:
            if not connection.transport.disconnecting:
                connection.sendLine(message)

class Lobby(MulticastServerFactory):
    protocol = Shuffle

    def startFactory(self):
        MulticastServerFactory.startFactory(self)
        self.game = None

    def stopFactory(self):
        MulticastServerFactory.stopFactory(self)
        self.broadcast(u"Server is going down for maintenance NOW!")

    def __init__(self, config):
        self.treshold = config['players']
        self.handsize = config['hand']
        self.decksize = config['deck']
        self.decklimit = config['decklimit']
        self.mana = config['mana']
        self.health = config['health']
        self.manainterval = config['replenish']
        self.healthinterval = config['regenerate']
        self.drawinterval = config['drawgain']
        self.initialdraws = config['initial-draws']
        self.draws = config['draws']

    def check_readiness(self):
        """We have been pinged from one of our clients to check if we can
        start the game.

        """
        ready = filter(operator.attrgetter('ready'), self.connections)
        assert len(ready) <= self.treshold, "bogus ready information"
        if len(ready) == self.treshold:
            for conn in self.connections:
                conn.ready = False # reset state now
            self.start_game(ready)

    def start_game(self, connections):
        """Start a new game session."""
        players = []
        for connection in connections:
            connection.ingame = player = Player(
                # set by session
                connection.name, connection.deck,
                # set by configuration
                self.handsize, self.mana, self.health,
                self.initialdraws, self.draws)
            players.append(player)

        self.broadcast(u"The battle begins..")
        self.game = Session(players)
        # broadcasting IDs
        # better not do this on `players` if someone connects in the meanwhile
        for connection in connections:
            if connection.ingame:
                connection.sendLine("You are #%d." % connection.ingame.id)
        # mana
        self.mana_beat = task.LoopingCall(self.game.award_mana)
        self.mana_beat.start(self.manainterval)
        # draw points
        self.draw_beat = task.LoopingCall(self.game.award_drawpoints)
        self.draw_beat.start(self.drawinterval, now=False)
        #XXX buffs
        # the main timer, used for high-resolution tasks
        self.beat = beat = task.LoopingCall(self.game.tick)
        beat.start(TICKINTERVAL
            ).addBoth(self.stop_game # notify the server when the game ends
            ).addBoth(self.mana_beat.stop  # kill mana and draw point tickers
            ).addBoth(self.draw_beat.stop) # when the game is over

    def stop_game(self, reason=None):
        """Stop the current session."""
        assert self.game is not None, "cannot stop game if not running"

        if reason is not None: # Twisted wants to tell us something
            print >>sys.stderr, reason
            self.broadcast(u"You broke it!")

        # nobody can possibly be playing after a game has stopped
        for connection in self.connections:
            connection.ingame = False

        # clean up the game
        self.game = None

def main(players, port=1030):
    from cardshuffle.tap import Options
    from twisted.internet import reactor
    factory = Lobby(Options())
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__ == '__main__':
    main(4)
