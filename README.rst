==============
 Card Shuffle
==============

**Card Shuffle** has originally been a custom map for *Warcraft 3* [1]_ [2]_
and features two wizard parties casting spells to extinguish the enemy team.

This game is a standalone port of the map.  It features an abstract simulation
of the match and a telnet interface to the game machinery.

.. [1] http://www.epicwar.com/maps/1414/
.. [2] http://www.epicwar.com/maps/128550/

Installing
==========

Install the package through the standard Python packaging mechanisms::

  python setup.py install

Setuptools will automatically pull in Twisted_ which provides the networking
part of the software.  It is built against Python 2.6.

.. _Twisted: http://twistedmatrix.com/trac/

You can then run a server using ``twistd`` which will listen for incoming
connections on port 1030 by default::

  twistd cardshuffle

Playing
=======

When you connect to a Card Shuffle server you start with no cards associated to
you.  While I strongly advise rolling your own custom deck you can let the
server generate a deck randomly for you by typing ``random``.  You can always
see which players are connected to the server by issuing ``list``.

Once your deck is complete (and satisfies the conditions imposed by the server)
you can type ``ready``.  If there are enough players marked as ready the server
will start a new match. See ``players`` for information on how the teams ended
up.

To uniquely identify every character on the battleground there is a number
attached to her -- the so called **field ID**.  Keep that in mind because
spells such as *Fireball* (or any other direct attack spell for that matter)
require an explicit target to be cast.

There are three significant quantities you should keep an eye on: health, mana,
and draw points (*HP*, *MP*, and *DP* respectively.)  You can always see those
values by typing ``stats`` or glimpse upon other players by typing ``stats N``
where *N* is the field ID of the player.

Your **health** determines how vital you are.  Once your health points drop to
zero you are *dead* and can not continue participating in the game.  **Mana**
is spent when invoking magic; almost all cards require you to sacrifice some
mana in order to use them.  Your **draw points** allow you to load your hand.
You will only ever draw cards which you have added to your deck.  Use ``hand``
to see your current inventory.

When you wish to cast a spell which you have on your hand you have to type its
slot followed by any arguments it might require to work.  For example, invoking
a *Fireball* spell which you have in your hand in position 1 on another player
with the field ID 4 you have to type ``1 4``.

The game was built with **spectators** in mind: if you do not feel like
participating in the game you are free to omit flagging yourself as ready and
you will receive broadcasts like all other players and can issue passive
commands as well.

Try ``help`` to see a short description of commands you can use if you feel
lost.

Hacking
=======

I have tried to separate the game logic from the networking part because I
would love to control the game through a full-fledged GUI some day in the
future.  If you feel like hacking something up please contact me.

The software was written without any fancy string building facilities to allow
easy localization.
