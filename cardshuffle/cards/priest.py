# Copyright (C) 2010 Robert Lehmann

from cardshuffle.cards import Card

class Heal(Card):
    mana = 20
    damage = -20
    desc = "Heal your target."
    tags = "light"
