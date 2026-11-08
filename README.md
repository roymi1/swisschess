# SwissChess

This is a program or tool that is meant to manage a chess tournament in the swiss system.

## Usage

Currently it is only built as an API, no main program, menus or GUI made yet.
main1.py was a one-time file done for start-up of data.

## Overview

This program supports the main rules of the swiss system for tournaments:
- There is a fixed list of participants during the whole tournament, from first round to last round
- The number of rounds is announced at the beginning
- We will use the ELO or chess.com rating of players to help with pairing; this is more relevant to the beginning of the tournament, before
we have score and buccholz information from the tournament itself.
- In each round, each player plays against an opponent who is another player; one plays with the white pieces and the other with black pieces.
- The winner gets 1.0 point after the games and the loser gets 0.0 or nothing. If the game ends with a draw, every player get 0.5 points.
- Starting from the second round, every player will get an opponent with the score (number of points) equal or close as much as possible.
- Player will never be paired against an opponent that he has already played in this tournament.
- We will try to balance for each player, the number of games as white with the number as black, and make them close as possible.
- If the number of participants is odd, each round there will be a "bye" - player with no game. The player will be selected based on lowest rating or score, the bye will get 1.0 points for this round, and no player will be bye twice in the tournament.

## API Usage: 

Starting a new tournament:
import tournament
t = tournament.Tournament("Cork site chess 2026", 7)
t.load_players("chess1.csv")
t.sort_players()
t.report_players("all_players.csv")
t.save_data("round0.json")

Loading an existing tournament from a saved file:
from tournament import Tournament
t2 = Tournament.__new__(Tournament) 
t2.load_data("round0.json")
t2.report_players("players.csv")
t2.pair_round(1)
t2.all_rounds[0].report_games(tour=t2)

