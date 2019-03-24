# 4D Blocks
This is a little game I wrote in college, which is a 4-dimensional
Tetris clone. So like Blockout, which is a 3D Tetris clone, only
there's another degree of freedom. So like in Tetris, blocks drop
down and you move them left and right, and in Blockout also up and down,
here you get one direction more.

Here's a screenshot of the game:
![screenshot](screenshot.png?raw=true)

To visualize the 4th dimension, 3d slices (akin to Blockout) are
shown of the 4d space. So it kind of looks like you're playing a
few instances of Blockout simultaneously.

You can also rotate the blocks in 90 degree steps. In Tetris there's
a single rotation axis and in Blockout there are three. In 4D space,
there are no longer axes of rotation (an axis keeps one direction in
place), but planes of rotation (a whole plane is kept in place by the
rotation), and there are six different (orthogonal) planes. You'll find
that in the way the space is shown as slices, three of the rotations
look like "normal" 3D rotations (they keep the forth dimmension untouched),
and three other will generally affect the fourth dimension, and distribute
parts of a block at different coordinates, so in different slices (so you
can kind of teleport part of a block to a different 3d slice with such a
rotation).

In the view you have the 3d slices with a helper grid in them, the colored
blocks, there's also a shadow pattern shown below the falling block to show
where exactly it'll land. In the corner the game displays score and the next
block that'll appear.

The rules are otherwise similar to Tetris and Blockout.

The objective is to gain as high a score as possible.
The score is increased by tho ways: whenever a block is dropped,
the score increases by 10. And when one or more layers of cubes are formed,
they are all removed and the score increases by `<numer of layers>^2 x 20`.
When blocks pile up so that there's no space on top to place the next block,
the game ends. Note, that a layer means all the cubes at the same height,
so it's 3d (it'll look like flat layers in all slices at the same height).

## Running the game
The game requires python2, along with the following python packages:
* numpy
* PyFTGL
* pygame
* PyOpenGL

Those in turn require system packages (OpenGL, FTGL, and SDL).
I've only tested the game on GNU/Linux, but it might run on other OSes.
Once you have the required packages, you can run the game with:

    python2 main.py

## Controls
Six keys/ key combos are used to move a block around in the six directions,
and twelve are used for rotating clock-wise and counter clock-wise in the
six axes. There's also a key for speeding up movement and one that
immediately drops the block.

They are configurable and support also gamepad buttons. You can
check default bindings and change them in the menu, which is accessed by
pressing Escape. Menu is navigated with the keyboard: Escape goes back or
closes the menu, Enter accesses an entry, left and right toggle between
values, up and down move between menu items. Note there's a bug that the
resume option doesn't work, just press Escape to resume the game.

## Notes on the code
The code is pretty old (it was made in 2012 I think). It uses the obsolete
Python 2 and obscure stuff like FTGL. It's also not written well. To start,
the code isn't formatted well, it's messy with e.g. lots of global variables,
code duplication, it freaking uses `eval` and `exec` (the `exec` is benign, the
`eval` one is in reading settings, so it allows for arbitrary code execution
via a text file, pretty lame). I was still learning a lot of things back then
and also didn't have much time. There's certainly room for improvement and
I might clean it up some time. For the time being, I'm placing it here as is.

On the upside, there's quite a lot of comments in the code, so maybe it'll
be useful to someone.

Here's a short summary of the files:
* `game.py` - Main game code. This file could be split in a few more, but
  anyway, it contains the game state in many global variables plus a ton
  of functions, mostly various opengl handling ones and callbacks for various
  things like screen refresh or input.
* `input_dev.py` - Input device (keyboard and gamepad) handling, including
  key binding.
* `key_num.py` - Constants used by the key binding code.
* `logic.py` - Contains the logic code for moving blocks, rotating them,
  detecting collisions, detecting game over and layer clearing. This I think
  might be of special interest for those intrigued by the workings of this game.
* `main.py` - Entry point, just sets up pygame and runs `game.main`.
* `menu.py` - Generic menu state machine handling.
* `settings.py` - Settings file handling. The code is pretty bad, it serializes
  data by writing output of `repr`, and then deserializes by `eval`ing it.
