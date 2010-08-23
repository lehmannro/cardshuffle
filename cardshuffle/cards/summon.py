# Copyright (C) 2010 Robert Lehmann

from cardshuffle.cards import Card

class Summon(Card):
    health = 1
    damage = 0
    speed = 1
    def apply(self, caster, args):
        caster.game
        pass #XXX create summon

class SummonImp(Summon):
    tags = "demonology"
    health = 20
    mana = 15
    damage = 5
    desc = "Summons an Imp."
