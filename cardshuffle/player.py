# Copyright (C) 2010 Robert Lehmann

import random

class Player(object):
    def __init__(self, name, deck, handsize, mana, health, draws):
        self.name = name
        self.deck = deck[:]
        self.max_mana = mana
        # managed properties
        self.mana = 0
        self.health = health
        self.draws = draws

        # We could possibly deal all cards but players might wish to draw cards
        # at their leisure, eg. to avoid spells on their hand.
        ## self.hand = random.sample(self.deck, handsize)
        self.hand = [None] * handsize

    @property
    def alive(self):
        return self.health != 0

    #XXX this should be wrapped in managed attributes
    def award_mana(self):
        self.mana = min(self.mana + 1, self.max_mana)
    def award_drawpoint(self):
        #XXX rules for draw points
        self.draws += 1

    def inflict(self, damage):
        self.health = max(self.health - damage, 0)

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
