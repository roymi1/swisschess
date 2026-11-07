player module and Player object

player module player.py contains the Player object with the information attributes relevant to his tournament record:

serial - will be its serial number in this tournament, from 1 to the number of participants
name - a string with the player full name
rating - a number that represents the player pre-expected playing level. Player with no know rating will be considered 1100.0 for rating.
score - will be the player current score (sum of points for past rounds)
buchholz - is the sum of the score of the player's past opponents. It is used as a secondary sort criteria after the score, to evaluate the player's quality of points.
percentage - is the score divided by number of games, so it's the relative achivement.
colorbal - is the number of previous games played as white minus the number of games as black, so the preferred color for next game will be
the color least previously given. If the numbers are equal, colorbal will be the 0.5 color of 
the player's last game - if last game was white, the colorbal will be 0.5 and if black, colorbal will be -0.5. 
The colorbal will be used for next round pairing - will try to match player with a positive colorbal with one with a negative, if possible within the same score group;
and the player will highest colorbal will be black (otherwise the highest score will get its "preferred" color)..
results - the list of scores or the player's games, ordered by rounds.
email - E-mail of the players
opponents - list of past opponents that the player played (was was paired) against
games - list of Match records for past games

the following methods are available:
calculate_score: calculates the total score of the player so far
calculate_buchholz: calculates the sum of scores of the player's opponents so far. This is a secondary sorting criterion after the player's score.
