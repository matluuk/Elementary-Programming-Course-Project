# Elementary-Programming-Course-Project
Course projet for elementary programming. There were several options where to choose from. 
I coose to make a game called A Wee Bit Miffed Ducks.

## Files I have made.
main.py
all files in kentat folder
images ritsa.png and tausta.png
some modifications to haravasto2.



# Assignment for the cource project

## A Wee Bit Miffed Ducks

The ducks are miffed! But why, or to whom? Well, we'll leave that up to your imagination. Regardless, there is only one conclusion: the ducks have to blast every single one of their enemies off the face of the earth. Obivously the most efficient way to do that is to launch oneself with a sling and crash into the target. In other words, you'll get to implement your own version of a certain famous Finnish mobile game. Naturally it will be simplified quite a bit. After all, the ducks themselves aren't even angry, just a bit miffed.

## Game Setup
Game window must have a place for launching ducks and also have destroyable targets. In addition, there must be obstacles which the ducks are unable to fly through. The player should also be able to see the amount of remaining ducks and other things about the game's state.
The map can be read from a map file which has the positions for targets and obstacles, as well as the number of available ducks. Each map also defines the filename of the next map. There is also another game mode where a random map is generated when the game is started. We recommend using the code base from the box dropping task in exercise 4 as a basis for this feature.

## Gameplay
Player launches ducks one at a time using the mouse, trying to hit and destroy targets. Stage is cleared if player destroys all targets before running out of ducks. Targets are destroyed when hit by a duck. If the duck hits an obstacle it will either stop or bounce (your choice, but the latter is harder to implement). The duck will also stop if it hits the ground. Once a duck has stopped, the player can launch a new one, provided there's ducks left.

## Ending
A stage can end in two ways:
Player wins if all targets are destroyed.
Player loses if they have run out of ducks and there are remaining targets.
The game must have at least two separate stages, and random stage generation. Player wins the game by passing each stage.
After passing a stage, player must be able to proceed to the next stage.
If a player loses in a stage, stage must be reset and player can try it again.
The random mode is enabled from the command line, or from a text-based menu. This mode continues by randomizing new stages until the player loses.

## Gameplay Features
The game must include at least the following features for ensuring comfortable gameplay experience.
Gravity: Ducks must come down sooner or later, instead of floating infinitely.
Solid objects: Ducks cannot pass through objects, unless they are intended to break (such as (possu)). Simply put: ducks must stop at obstacles.
Ducks can be launched either by dragging with a mouse (slingshot) or by adjusting angle and power with buttons (cannon).
Ducks' flying speed and direction are calculated from launching angle and power.
When using mouse input, angle and power are determined by cursor's position in relation to starting position.
(possu) must be destroyed upon impact.
## Acceptable Implementation

In order for your project to be accepted, it needs to show the understanding of the course contents. Below is a checklist you can use to determine whether you've fulfilled the requirements.
The game correctly implements the rules described above.
There's gravity that prevents the ducks from flying forever.
Game state is displayed to the player in the user interface.
Ducks must only be able to be launched from a dedicated launching position. An already launched duck cannot therefore be launched again mid-air or after coming to a stop.
A new duck must be prepared either automatically or by clicking/pressing manually after each shot (if ducks still remaining).
Next stage is entered by passing the previous one. Upon passing every stage, the game ends in player's victory.
The game includes a main menu or command line arguments which the player can use to choose between playing premade stages and randomly generated ones.
Missing or errors in any of these will bounce the course project back to you for improvements.
## Graphics

We've created a small helper library for creating graphics in a game window with more or less the same means as everything else we've done in the course - by calling functions. You don't have to use this library but the game must have graphics, implemented one way or another. The library module has rather extensive docstrings that should provide assistance about its use. Some additional instructions can be found below.
For historical reasons the library is called Sweeperlib because it was initially made for the minesweeper project. We've expanded it with features that are needed for tossing ducks.
Since we don't want to slander any particular animal, we have decided to present the targets as boxes with an X. Feel free to make your own target sprite if you want to.
