# Copyright (C) 2010, 2011 Robert Lehmann

import random
import operator

class Player(object):
    def __init__(self, name, deck, handsize, mana, health, draws):
        self.name = name
        self.deck = deck[:]
        self.max_mana = mana
        self.max_health = health
        # managed properties
        self._mana = 0
        self._health = health
        self._draws = draws

        # We could possibly deal all cards but players might wish to draw cards
        # at their leisure, eg. to avoid spells on their hand.
        ## self.hand = random.sample(self.deck, handsize)
        self.hand = [None] * handsize

    @apply
    def mana():
        fget = operator.attrgetter('_mana')
        def fset(self, value):
            self._mana = min(max(value, 0), self.max_mana)
        return property(fget, fset)

    @apply
    def health():
        fget = operator.attrgetter('_health')
        def fset(self, value):
            alive = self.alive
            self._health = min(max(value, 0), self.max_health)
            if alive != self.alive:
                pass #XXX player died (or was resurrected), notify someone?
        return property(fget, fset)

    @apply
    def draws():
        fget = operator.attrgetter('_draws')
        def fset(self, value):
            self._draws = min(max(value, 0), self.max_health)
        return property(fget, fset)

    @property
    def alive(self):
        return self.health != 0

    def draw(self):
        if None not in self.hand or not self.draws:
            return # hand is full or drawing is not permitted, exit gracefully
        self.draws -= 1
        slot = self.hand.index(None)
        card = random.choice(self.deck)
        self.hand[slot] = card()
        #XXX check for composable cards
        return card

    def use(self, slot, args=None):
        if not 1 <= slot <= len(self.hand):
            return # invalid slot
        slot -= 1
        if self.hand[slot] is None:
            return # selected slot is empty, exit gracefully

        # Use card and put its remains into its slot. This is ``None`` usually
        # but could be the same card if it still has charges left. Cards may
        # also decide to return wholly different cards.
        self.hand[slot] = self.hand[slot].apply(self, args)

    def discard(self, slot):
        self.hand[slot-1] = None
