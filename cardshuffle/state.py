# Copyright (C) 2012 Robert Lehmann

class GameState(Exception): pass

class OutOfMana(GameState): pass
class OutOfDraws(GameState): pass
class HandIsFull(GameState): pass
class EmptySlot(GameState): pass

class PlayerDied(GameState): pass
class GameOver(GameState): pass
