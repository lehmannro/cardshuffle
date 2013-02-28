# encoding: utf-8
# Copyright (C) 2010, 2011 Robert Lehmann

from cardshuffle.cards import Card

from twisted.protocols import basic

import functools
import itertools
import random
import string

PLAYER = itertools.count(1)
VALIDCHARS = string.ascii_letters + string.digits + ' '
# must cover "Player 1" etc.

def players_only(fun):
    """Only triggers for connections which are part of the current game."""
    @functools.wraps(fun)
    def wrapper(self, args):
        if self.ingame:
            return fun(self, args)
        return u"This command is only available for players."
    return wrapper

def ingame(fun):
    """Only triggers when there is a game going on."""
    @functools.wraps(fun)
    def wrapper(self, args):
        if self.factory.game:
            return fun(self, args)
        return u"This command is only available during game sessions."
    return wrapper

def targetable(fun):
    """Allows commands to be used for oneself or other players."""
    @ingame
    @functools.wraps(fun)
    def wrapper(self, args):
        if self.ingame and not args:
            target = self.ingame
        else: # we must not be necessarily be part of the current game
            try:
                target = self.factory.game.entities[int(args)-1]
            except (IndexError, ValueError):
                return u"This command requires a valid target."
        return fun(self, target)
    return wrapper


class Shuffle(basic.LineOnlyReceiver):
    """Line-based text protocol to play the game and join the lobby server."""
    delimiter = '\n'

    def __init__(self):
        """A client connected. For your convenience he gains a nickname which
        is likely unique (but does not have to be.)  Players need to set their
        deck and mark themselves as ready before they are eligible to join the
        next game.

        """
        self.name = u"Player %d" % PLAYER.next() # need not be unique
        self.ready = False
        self.ingame = False
        self.deck = []

    def sendLine(self, data):
        """Send a message to a client encoded in UTF-8."""
        basic.LineOnlyReceiver.sendLine(self, data.encode('utf-8'))

    def lineReceived(self, data):
        """A client wishes to interact with the server.

        His message shall be sent verbatim to all other clients if prefixed
        with a colon or otherwise dispatched to the responsible command handler
        beginning with ``command_``.

        For programming convenience every exclusively numeric command is
        forwarded to `special_use` indicating the player wishes to use an item
        from his inventory.

        """
        data = data.strip().decode('utf-8', 'ignore')
        if data.startswith(':'):
            # server-wide messages
            #XXX party-only messages
            self.factory.broadcast(u"%s: %s" % (self.name, data[1:]))
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
        if len(self.deck) != self.factory.decksize:
            return (u"Your deck does not match the expected size of %d." %
                    self.factory.decksize)
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

    @ingame
    def command_players(self, args):
        """Show all players in the current game."""
        self.sendLine(u"East fraction:")
        self.list_players(self.factory.game.west)
        self.sendLine(u"West fraction:")
        self.list_players(self.factory.game.east)

    def list_players(self, players):
        for player in players:
            if player.alive:
                self.sendLine(u"❥ %s #%d [%d/%d HP]" %
                    (player.name, player.id, player.health, player.max_health))
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
        #XXX actually fill up the deck, do not replace it
        stack = list(Card.all())
        self.deck = deck = random.sample(stack * 20, self.factory.decksize)
        #                                      ^^^^
        #XXX hack to make up for our lack of cards
        self.list_cards(deck)

    def command_clear(self, args):
        """Erase your deck."""
        self.deck = []

    def command_tags(self, args):
        """Show all available tags."""
        for tag, taggeds in Card.by_tag.iteritems():
            self.sendLine(u"· %s (%d cards)" % (tag, len(taggeds)))

    def command_show(self, args):
        """Display your selected deck."""
        self.list_cards(self.deck)

    def command_search(self, args):
        """Search for a card by its name."""
        if len(args) < 3:
            return u"Search terms must be at least three characters."
        self.list_cards(card for card in Card.all()
            if args.lower() in card.name.lower())

    def command_tag(self, args):
        """Show cards by tag."""
        #XXX error handling
        self.list_cards(Card.by_tag.get(args, []))

    @players_only
    def command_draw(self, args):
        """Draw a card (players only.)"""
        new = self.ingame.draw()
        if new:
            self.list_cards([new])

    @players_only
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
        #XXX caching
        commands = [(name[len('command_'):], attr.__doc__)
                    for name, attr in
                    self.__class__.__dict__.iteritems()
                    if name.startswith('command_')]
        commands.append(("N ...", u"Use card at slot ‘N’;"
            u" might require further arguments (players only.)"))
        for name, doc in commands:
            self.sendLine(u"%-8s  %s" % (name, doc))

    @players_only
    def special_use(self, args):
        slot, args = args # slot is stored in args
        self.ingame.use(slot, args)

    @players_only
    def command_discard(self, args):
        #XXX error handling
        self.ingame.discard(int(slot))
