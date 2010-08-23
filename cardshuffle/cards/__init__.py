# encoding: utf-8
# Copyright (C) 2010 Robert Lehmann

import re
from collections import defaultdict

TITLECASE = re.compile(r'(?<=.)([A-Z])')

class Card:
    by_tag = defaultdict(list)
    class __metaclass__(type):
        def __new__(meta, name, bases, clsdict):
            clsdict.setdefault('name', TITLECASE.sub(r' \1', name))
            clsdict['tags'] = tags = clsdict.get('tags', "").split()
            for base in bases:
                tags.extend(base.tags)
            new = type.__new__(meta, name, bases, clsdict)
            for tag in tags:
                new.by_tag[tag].append(new)
            return new

    @classmethod
    def all(cls):
        #XXX caching
        children = cls.__subclasses__()
        for child in children:
            for sub in child.all():
                yield sub
        if not children:
            yield cls

    tags = ""
    desc = ""
    charges = 1
    mana = 0

    def apply(self, caster, args):
        """Use a card."""
        if caster.mana < self.mana:
            return # out of mana, exit gracefully
        self.charges -= 1
        if charges > 0:
            return self
        return None # empty slot

# activate all cards
import cardshuffle.cards.offensive
import cardshuffle.cards.summon
