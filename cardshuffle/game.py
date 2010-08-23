# encoding: utf-8
# Copyright (C) 2010 Robert Lehmann

import itertools
import random

MAXTICKS = 65536

class GameOver(StopIteration): pass

class Session(object):
    def __init__(self, players):
        """A single session of Card Shuffle, but for the networking part. It
        works like a simulation in the way that you need to keep the game
        progressing yourself (by using *ticks*).

        """
        self.players = players

        # East party will always receive surplus players
        self.west = players[:len(players)/2]
        self.east = players[len(players)/2:]

        self.entities = []

        for player in players:
            player.game = self
            self.identify(player)

        self.ticks = 0
        self.summons = []

    def identify(self, entity):
        if not hasattr(entity, 'id'): # noop if already registered
            # woo, O(1) over entity in self.entities
            entity.id = len(self.entities)+1
            self.entities.append(entity)
    def __getitem__(self, id):
        return self.entities[id-1]

    def tick(self):
        tick = self.ticks

        # move summons along
        for summon in self.summons:
            pass

        # game over heuristics
        if 0:
            raise GameOver

        #XXX is counting ticks really neccessary?
        # next
        self.ticks = (tick + 1) % MAXTICKS

    def award_drawpoints(self):
        """Hand out draw points to all players."""
        for player in self.players:
            player.award_drawpoint()
    def award_mana(self):
        """Hand out one mana point to each player."""
        for player in self.players:
            player.award_mana()
