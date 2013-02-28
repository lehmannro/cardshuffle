# Copyright (C) 2010 Robert Lehmann

from cardshuffle.cards import Card

class TomeOfMagic(Card):
    tags = "dark"
    def apply(self, caster, args):
        caster.health -= 50
        caster.max_mana += 50
