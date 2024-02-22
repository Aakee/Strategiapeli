# Project 'Strategiapeli'

## About the repository

This repository includes a game called simply Strategiapeli ('Strategy Game' in English), a project work conducted on Spring 2017 on a Python programming course at Aalto University (Basic Course in Programming Y2, CS-A1121). It is a *Fire Emblem* like strategy game between a player and computer: both players play turn-wise controlling all their characters with different abilities, attacks, and stats.

The documentation, as well as some in-game text, is written in Finnish.


## About this branch

This branch, called *original-game*, holds the source code almost exactly as I programmed it on Spring 2017 -- the only fixes I have made to it since then are some minor bug fixes. Additionally, this readme was written later. The game was imported to GitHub on February 2024, and is intended to be kept unmodified, meaning that this branch pretty much shows the legacy game.


## Dependencies

The game needs PyQt5 to run. You can install it with
  `python -m pip install pyqt5`
(or similar).


## How to run

The game has been programmed and tested on Windows. While it might work on different platforms as well, it is not guaranteed.

Change the working directory to src (important, as the game handles files relative to the working directory), and run the script `main.py`, e.g. with `python ./main.py`. The actual command depends on your Python installation.


## How to play

These are not exhaustive instructions; rather, this constitutes as a coarse guide to get you started.

### Main window

When you start the game you see the main window. The game automatically loads the game saved to 'src/save.txt'. The game board is showed alongside all characters.

The different menus are:

- **Game**
  - **Save game:** Save the current game state (character placement and HP) to a file. Note that the save format does not save the information of whose turn it is and which characters have been moved. This can be used effectively to savescum repeteatedly -- but you wouldn't do that, would you?
  - **Load game:** Load a previously saved game. This discards the current game. The turn will be set to the player and all characters are set to be unmoved, regardless if they were that way when the game was saved.
  - **End turn:** If it is players turn, end the turn with all remaining unmoved characters skipping their turn and remaining in the place they currently are. It will now be computer's turn.
  - **Quit game:** Quite the game without saving.
- **Show**
  - **Infowindow:** Opens the infowindow. Can be used if the infowindow is accidentally closed.

### Infowindow

The infowindow is automatically opened when the game is started. It shows characters' current placement and HP.

If you click one of the character icons in the infowindow, a new character window is opened. This window shows additional information of the character:

- Available attacks
- Available skills
- Current stats

### Console

Information about the game events are printed to console (in Finnish).

### Characteres

#### Moving the characters

Click one of your characters, colored blue. The squares where you can move with this character are highlighted. Click one of these squares to move the character there. After this, a window is opened asking what you want the character to do. You can choose one of the actions, or close the window. If you close the window, the character's turn is not ended, and it can move and choose action later again.

A character can move through asquare occupied by a friendly character but can not land on it. A character cannot move through nor land on a square occupied by a enemy character.

#### Attacking with your character

Move your character and choose an attack from the list. Different attacks have different ranges, powers and accuracies, which you can see by opening the character window from infowindow. Choose an attack to see which enemy characters you can attack to -- these possible enemy squares are highlighted in red. Click one of these squares, and a confirmation window is opened, showing the probability the attack will hit, and the damage it will do assumed the attack lands. Finally, click **Confirm** to do the attack.

When you have attacked (regardless if the attack landed or not), the character will be colored gray to signify that its turn has ended. It cannot move or do an action again before the player's next turn. If you at any point cancel the attack, the turn is not ended.


#### Using a skill

Similarily to using an attack, you can choose a skill from the list. Some of the skills characters have are passive, meaning that they will either be active all the time, or activated, meanining that they must be choosed and used similarily to attacks. In contrast to attacks, skills can target one or multiple allies (depending on the skill). When you choose a skill, the tiles you can use it on turns green. If the skill has a single target, click on that square and select **Confirm** to use the skill on that character. If the skill can have multiple targets, click any green square and select **Confirm** to use the skill on all allies on the green squares.

As with attacks, the character's turn ends when it has activated a skill.


#### Passing the turn

You can choose Pass to end the character's turn without using an attack or a skill. Note that it is equivalent to choose **Game** -> **End turn** and to select **Pass** on all characters individually.


#### Losing a character

When a character's HP drops to zero, it dies and is immediately removed from the board.


### Terrains

The different-colored suqres in the board signify different terrains:

- **Light yellow:** Plain. No special effect.
- **Gray:** Mountain. No special effect.
- **Brown:** Wood. No special effect.
- **Green:** Forest. Moving through forest takes more steps than on normal terrains. Additionally, reduces speed of a character standing on forest.
- **Yellow:** Sand. Takes even more steps to move through and reduces speed even more than forest.
- **White:** Snow. Functions the same way as forest.
- **Blue:** Water. Characters cannot move through water, though they can attack over with ranged attacks.
- **Black:** Wall. Characters cannot move through walls, though they can attack over with ranged attacks.

Characters with certain skills can avoid these restrictions.


### Winning or losing the game

A player loses the game when all their characters are dead. The other player wins the game.


## Additional game rules and documentation

You can find the documentation in Finnish in "/Suunnitelmat & dokumentointi". This branch includes no English documentation.


## Last updated

The source code was last updated on May 2017 and imported to GitHub on February 2024. This readme was last updated on February 2024.