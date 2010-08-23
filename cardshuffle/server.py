# encoding: utf-8
# Copyright (C) 2010 Robert Lehmann

from cardshuffle import game, cards
from cardshuffle.player import Player

from twisted.internet import reactor, protocol, task
from twisted.protocols import basic

import functools
import itertools
import operator
import random
import string

DECKSIZE = 15
HANDSIZE = 6
MAXMANA = 200
MAXHEALTH = 200
TICKINTERVAL = 0.02 # 50 fps
MANAINTERVAL = 1
DRAWINTERVAL = 30
REGENINTERVAL = 5

PLAYER = itertools.count(1)
VALIDCHARS = string.ascii_letters + string.digits + ' '
# must cover "Player 1" etc.

def ingame(fun):
    """Only triggers for connections which are part of the current game."""
    @functools.wraps(fun)
    def wrapper(self, args):
        if self.ingame:
            return fun(self, args)
        return u"This command is only available for players."
    return wrapper

def targetable(fun):
    """Allows commands to be used for oneself or other players."""
    @functools.wraps(fun)
    def wrapper(self, args):
        if self.factory.game:
            if self.ingame and not args:
                target = self.ingame
            else: # we must not be necessarily be part of the current game
                try:
                    target = self.factory.game.entities[int(args)-1]
                except (IndexError, ValueError):
                    return u"This command requires a valid target."
            return fun(self, target)
        else:
            return u"This command is only available during game sessions."
    return wrapper


class Shuffle(basic.LineOnlyReceiver):
    delimiter = '\n'
    def __init__(self):
        self.name = u"Player %d" % PLAYER.next() # need not be unique
        self.ready = False
        self.ingame = False
        self.deck = []

    def sendLine(self, data):
        basic.LineOnlyReceiver.sendLine(self, data.encode('utf-8'))

    def lineReceived(self, data):
        data = data.strip().decode('utf-8', 'ignore')
        if data.startswith(':'):
            # server-wide messages
            #XXX party-only messages
            factory.broadcast(u"%s: %s" % (self.name, data[1:]))
        else:
            command, args = (data.strip() + ' ').split(' ', 1) # nasty hack
            if not command:
                return # empty line
            args = args[:-1]
            method = 'command_'+command

            # special syntax for items :-)
            if command.isdigit():
                method = 'special_use'
                args = int(command), args

            # dispatch
            if hasattr(self, method):
                try:
                    ret = getattr(self, method)(args)
                except Exception, e:
                    #XXX distinguish between Exceptions and User Errors
                    import traceback; traceback.print_exc()
                    self.sendLine("Internal server error: %s" % (e,))
                else:
                    if ret is not None:
                        self.sendLine(ret)
            else:
                self.sendLine(u"Unknown command: %s" % command)

    def command_ready(self, args):
        """Mark yourself ready."""
        if self.factory.game:
            return u"A game is already in progress."
        if self.ready:
            #XXX toggle ready state
            return u"You were already marked as ready."
        if len(self.deck) != DECKSIZE:
            return (u"Your deck does not match the expected size of %d." %
                    DECKSIZE)
        self.ready = True
        self.factory.broadcast(u"%s became ready." % self.name)
        self.factory.check_readiness()

    def command_name(self, args):
        """Change your nickname."""
        if not args:
            return u"The `name' command requires a `nickname' parameter."
        if any(c not in VALIDCHARS for c in args):
            return (u"Names are only allowed to contain the following"
                    u"characters: %s" % VALIDCHARS)
        oldname = self.name
        if oldname == args:
            return # name has not changed
        self.name = args
        self.factory.broadcast(u"%s is now known as %s" % (oldname, args))

    def command_list(self, args):
        """Show all connected users."""
        self.sendLine(u"%d players currently connected:" %
            len(self.factory.connections))
        for connection in self.factory.connections:
            self.sendLine(u"%s %s" %
                (u"☐☑☒"[connection.ready+2*bool(connection.ingame)],
                 connection.name))

    def command_players(self, args):
        """Show all players in the current game."""
        if self.factory.game:
            self.sendLine(u"Right fraction:")
            self.list_players(self.factory.game.west)
            self.sendLine(u"Left fraction:")
            self.list_players(self.factory.game.east)
        else:
            return u"There is no game going on."

    def list_players(self, players):
        for player in players:
            if player.alive:
                self.sendLine(u"❥ %s #%d [%d/%d HP]" %
                    (player.name, player.id, player.health, 0))
                #                                ^
                #XXX store maximum health in players
            else:
                self.sendLine(u"☠ %s" % player.name)

    def list_cards(self, cards):
        for card in cards:
            self.sendLine(u"· %s [%s] %s" %
                (card.name, u"/".join(card.tags), card.desc))

    def command_random(self, args):
        """Fill up deck with random cards."""
        stack = list(cards.Card.all())
        self.deck = deck = random.sample(stack * DECKSIZE, DECKSIZE)
        #                                      ^^^^^^^^^^
        #XXX hack to make up for our lack of cards
        self.list_cards(deck)

    def command_tags(self, args):
        """Show all available tags."""
        for tag, taggeds in cards.Card.by_tag.iteritems():
            self.sendLine(u"· %s (%d cards)" % (tag, len(taggeds)))

    def command_show(self, args):
        """Display your selected deck."""
        self.list_cards(self.deck)

    def command_search(self, args):
        """Search for a card by its name."""
        if len(args) < 4:
            return u"Search terms must be over three characters."
        self.list_cards(card for card in cards.Card.all()
            if args.lower() in card.name.lower())

    def command_tag(self, args):
        """Show cards by tag."""
        #XXX error handling
        self.list_cards(cards.Card.by_tag.get(args, []))

    @ingame
    def command_draw(self, args):
        """Draw a card (players only.)"""
        new = self.ingame.draw()
        if new:
            self.list_cards([new])

    @ingame
    def command_whoami(self, args):
        """Show your field ID (players only.)"""
        return u"You are #%d, %s." % (self.ingame.id, self.name)

    @targetable
    def command_hand(self, target):
        """Show a player's hand."""
        if target != self.ingame:
            self.sendLine(u"%s's hand:" % target.name)
        for slot, card in enumerate(target.hand, 1):
            if card:
                self.sendLine(u" %d. %s (%dMP)" % (slot, card.name, card.mana))
            else:
                self.sendLine(u" %d. empty" % slot)

    @targetable
    def command_stats(self, target):
        """Show game information about a player."""
        if target != self.ingame:
            self.sendLine(u"%s:" % target.name)
        self.sendLine(u" HP: %d / MP: %d / DP: %d" %
            (target.health, target.mana, target.draws))

    def command_help(self, args):
        """Show this command documentation."""
        for name, attr in self.__class__.__dict__.iteritems():
            if name.startswith('command_'):
                self.sendLine(u"%-8s  %s" %
                    (name[len('command_'):], attr.__doc__))

    @ingame
    def special_use(self, args):
        slot, args = args # slot is stored in args
        self.ingame.use(slot, args)

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

    def __init__(self, players):
        self.treshold = players

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
                connection.name, connection.deck,
                HANDSIZE, MAXMANA, MAXHEALTH) #XXX configurable
            players.append(player)

        self.broadcast(u"The battle begins..")
        self.game = game.Session(players)
        # mana
        self.mana_beat = task.LoopingCall(self.game.award_mana)
        self.mana_beat.start(MANAINTERVAL)
        # draw points
        self.draw_beat = task.LoopingCall(self.game.award_drawpoints)
        self.draw_beat.start(DRAWINTERVAL, now=False)
        #XXX buffs
        # the main timer, used for high-performance tasks
        self.beat = beat = task.LoopingCall(self.game.tick)
        beat.start(TICKINTERVAL
            ).addBoth(self.stop_game # notify the server when the game ends
            ).addBoth(self.mana_beat.stop  # kill mana and draw point tickers
            ).addBoth(self.draw_beat.stop) # when the game is over

    def stop_game(self, reason=None):
        """Stop the current session."""
        assert self.game is not None, "cannot stop game if not running"

        if reason is not None: # Twisted wants to tell us something
            self.broadcast(u"You broke it!")

        # nobody can possibly be playing after a game has stopped
        for connection in self.connections:
            connection.ingame = False

        # clean up the game
        self.game = None

def main(players, port=1030):
    factory = Lobby(players)
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__ == '__main__':
    main(4)
