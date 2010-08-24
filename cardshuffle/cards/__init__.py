# encoding: utf-8
# Copyright (C) 2010 Robert Lehmann

import re
from collections import defaultdict

TITLECASE = re.compile(r'(?<=.)([A-Z])')

class Card:
    by_tag = defaultdict(list)
    class __metaclass__(type):
        def __new__(meta, name, bases, clsdict):
            # extract the card name from its class name if it was not
            # explicitly set
            clsdict.setdefault('name', TITLECASE.sub(r' \1', name))
            # transform its tags string into a list of tags
            clsdict['tags'] = tags = clsdict.get('tags', "").split()
            # ..and add all its superclass tags, too
            for base in bases:
                tags.extend(base.tags)
            # create the Card type
            new = type.__new__(meta, name, bases, clsdict)
            # add the card to all of its tags in the `by_tag` mapping
            for tag in tags:
                new.by_tag[tag].append(new)
            return new

    @classmethod
    def all(cls):
        """Return all cards known to the game engine."""
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
        assert self.charges > 0
        if caster.mana < self.mana:
            return # out of mana, exit gracefully
        self.charges -= 1
        if self.charges > 0:
            return self
        return None # empty slot

# activate all cards
import cardshuffle.cards.offensive
import cardshuffle.cards.summon
