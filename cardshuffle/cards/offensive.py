# Copyright (C) 2010 Robert Lehmann

from cardshuffle.cards import Card

class DirectAttackSpell(Card):
    damage = 0

    def apply(self, caster, args):
        target = caster.game[int(args)]
        new = Card.apply(self, caster, args)
        target.inflict(self.damage)
        return new

class Fireball(DirectAttackSpell):
    mana = 40
    damage = 50
    tags = "fire"
    desc = "Hurls a fiery ball."
