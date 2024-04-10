# Connections!
## Overview
This is a much improved Command Line Interface for the New York Times connections game!!!  
There are 4 groups of 4 words, and the objective is to find each of the 4 groups!

![img.png](basic_demo.png)

## Cheating
Cheating will be taken very seriously!!! This program includes a kernel level anti-cheat software
that will monitor any network traffic, all connected displays, and all connected microphones and cameras.
Does this seem dangerous for such a simple game? No! Cheaters is the enemy, anything to stop them! All games will
also be monitored for statistical outliers. **Anyone suspected of cheating will be banned and sent straight to jail!**

## Installation

Ensure `python > 3.5` is installed and included on your PATH  
Ensure `git` is installed and included on your PATH

### Terminal Compatibility
curses should work out of the box on any `mac` terminal or `linux` terminal.
If you are on `windows` you will need to run `pip install windows-curses`.
Even with that I have only managed to get it to work on windows using the 
`emulate terminal in output console` option in `Pycharm > run configuration`.
Alternatively installing wsl2 is relatively easy and should work like a charm.




To retrieve the repository run:
`git clone git@github.com:ConorMurphy21/Connections.git` in 
the directory you would like to install it to.


If you would like to contribute your own games, or share your game logs
to compare how well you did you can shoot me a message saying "pretty please may I 
be a connections contributor?", and I'll think about it 😛.

## How To Play
### Useful flags
run `python connections.py -h` for a comprehensive command guide,
this section will just give basic use-case tips

#### Generate game
`python connections.py -g`

#### Play any game
`python connections.py` will pick a good game for you

#### Play a specific game
Use `-a [username]` to specify the author, optionally `-n [number]` to specify the game number

#### Share a game with a friend
Use `-u [friend_username]` to temporarily play or generate as `[friend_username]`

#### Debugging
If for some reason your game seems bugged, or you are developing a feature use `-d`,
this doesn't provide any better debugging info it just prevents the script from interacting with git
(which can get annoying in these scenarios). Please avoid using this option if everything is working fine!

### In Game Controls
`[a-z]`: Select or Unselect word  
`?`: Guess currently selected words  
`\`: Clear currently selected words  
`!`: Shuffle all the words around  
`[1-9]`: Show previous guess `#n`  
`-`: Show previous previous guess  
`=`: Show next previous guess  
`:q`: Exit game  
`>`: Exit with Skip log

### Lives
If your guess was one away it will display `o` where your life used to be,
if you are more than one away it will display `x` where your life used to be.

## FAQ

#### Why not use TAB or ENTER instead of ASCII characters
Ensuring those codes work across OS requires I try them out on every OS.
Using ASCII ensures everyone can play!

#### Why not use both TAB and ENTER with ASCII for the systems you can test?
well... uhhh...

#### Why is it committing and pushing everytime I play the game? Doesn't this create an awful git history?
erm.....

#### Why are you using a logger to write game files?
ughh....

#### Why is the code full of magi--💥
That's all the time we have left for questions!
