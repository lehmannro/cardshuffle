# Copyright (C) 2010 Robert Lehmann

from cardshuffle.cards import Card

class DirectAttackSpell(Card):
    damage = 0

    def cast(self, caster, args):
        target = caster.game[int(args)]
        target.health -= self.damage

class Fireball(DirectAttackSpell):
    mana = 40
    damage = 50
    tags = "fire"
    desc = "Hurls a fiery ball."
