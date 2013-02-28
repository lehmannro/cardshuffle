# Copyright (C) 2010, 2011, 2012 Robert Lehmann

from cardshuffle.state import HandIsFull, OutOfDraws

import random
import operator


def managed_property(attr, maxattr, callback=None):
    fget = operator.attrgetter(attr)
    def fset(self, value):
        old_value = fget(self)
        new_value = min(max(value, 0), getattr(self, maxattr))
        setattr(self, attr, new_value)
        if callback:
            callback(self, old_value, new_value)
    return property(fget, fset)

class Player(object):
    def __init__(self, name, deck, handsize,
                 mana, health, draws, max_draws):
        self.name = name
        self.deck = deck[:]
        self.max_mana = mana
        self.max_health = health
        self.max_draws = max_draws
        # managed properties
        self._mana = 0
        self._health = health
        self._draws = draws

        # We could possibly deal all cards but players might wish to draw cards
        # at their leisure, eg. to avoid spells on their hand.
        ## self.hand = random.sample(self.deck, handsize)
        self.hand = [None] * handsize

    mana = managed_property('_mana', 'max_mana')
    def health_changed(self, old, new):
        if new == 0 and old != 0:
            pass #raise PlayerDied(self)
        elif old == 0 and new != 0:
            pass #raise PlayerResurrected(self)
    health = managed_property('_health', 'max_health', health_changed)
    draws = managed_property('_draws', 'max_draws')

    @property
    def alive(self):
        return self.health != 0

    def draw(self):
        if None not in self.hand:
            raise HandIsFull
        if not self.draws:
            raise OutOfDraws
        self.draws -= 1
        slot = self.hand.index(None)
        card = random.choice(self.deck)
        self.hand[slot] = card()
        #XXX check for composable cards
        return card

    def use(self, slot, args=None):
        if not 1 <= slot <= len(self.hand):
            raise ValueError # invalid slot
        slot -= 1
        if self.hand[slot] is None:
            return # selected slot is empty, exit gracefully

        # Use card and put its remains into its slot. This is ``None`` usually
        # but could be the same card if it still has charges left.  Cards may
        # also decide to decay into completely different cards.
        self.hand[slot] = self.hand[slot].apply(self, args)

    def discard(self, slot):
        self.hand[slot-1] = None
