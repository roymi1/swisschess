# Match module - games and rounds management module

## Overview

This file contains two classes: Match which describes a single module, and Round which describes
a round of games in the tournament.

## Match

Match object that describes a game, with the numbers (or objects) or players as white and black in
the game, and their results which are updated after the games: white_result and black_result.
The typical results for a chess games are:
white wins: white_result = 1.0, black_result = 0.0
Draw: white_result = 0.5, black_result = 0.5
Black wins: white_result = 0.0, black_result = 1.0
White technical win: white_result = "+", black_result = "-"
Black technical win: white_result = "-", black_result = "-"
Technical mutual loss: white_result = "-", black_result = "-"

For every practical use, a technical win ("+") is considered like 1.0 point, and a technical
loss ("-") is considered like 0.0 points. So these are the values returns by the methods 
white_score and black_score.

The method to_dict is called to return a dictionary when saving tournament data to a JSON file.

## Round

Round is the list of games played in a round of the tournament, where every player plays one game
(with the only exceptions of a bye player, when the number of active players is odd there is one
bye player every round who gets a techical "+", and if a player has quit the tournament then this
player is not matched any more).

report_games provides a list of all games played or to be played in a round, the report is not
the screen and optionally to a CSV file.

import_results reads a CSV file created by report_games and updates the already-paired games in
the round. Games are selected by the one-based Board column. Normal results may be 0, 0.5, or 1;
technical results may be + or -, and an empty score clears the result. Passing the tournament as
the ``tour`` argument also validates each player's serial number and name before applying results.

### Pairing

Pairing is stage after a round is over (or mostly over) and the list of matches or games for the
next round should be made.

pair_first_round: First round pairing is based on initial serial numbers, where n players are
divided to two halfs, each with n/2 player. In board 1, player number one plays against player 
number n/2 + 1, in board 2 player #2 against n/2 + 2 (with reverse colors to the previous game), 
player #3 against n/2 + 3 (with reverse colors to previous, so player #3 has the same color
as player #1) and so on.
