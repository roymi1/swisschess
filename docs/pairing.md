# Swiss system: Pairing for rounds after the first round

## High-level rules:
1. Every active player appear exactly once in each round.
2. No rematches of same two players.
3. Nobody receives a second bye.
4. Minimize score differences.
5. Follow the prescribed below floating direction.
6. Improve color balance.
7. Use Buchholz and serial number as deterministic tie-breakers.

## These are the stages of the pairing of rounds from round 2
These are the main stages:
- Pairing is done when asked by the user or called Tournament.pair_round(), after most of the results from previous rounds and games are known and tourtnament.last_round_played is equal to last_round_paired. 
However, there may be some unplayed games or missing results, they will be considered as 0.5 point each for pairing purpose only.
- If player have quit the tournament, they will no longer be matched in next rounds.
- Updating the status of players with up-to-date score, buchholz and color balance (colorbal) with tournament.update_players_data().
- If a player has equal number of games as white and black, his colorbal will be 0.5 the color he had in his last game,
(0.5 if it was white and -0.5 if it was black), so colorbal should not be 0 (unless player was bye in last round) preferably the player will get an opposite color next match. colorbal should not be 0. Unplayed games also count for color balance as we expect them to be completed later, technical results also count - do they depend only on previous pairing and not games results. 
- Sorting all players to groups by their current score. Within each group, players will be sorted by the higher buchholz or lower serial number.
- Pair the groups according to the score by this order: first the highest score, then the second highest score, and so on until, but not including the
median group (the one with 50% score from the number of games). Then move to the bottom: first the lowest score group, then the second lower and so on,
until the median group and then pair it too.
For example, after two rounds: first pair the group of 2.0 points, then 1.5 point, then 0 points then 0.5 points and finally 1.0 point.
- If the number of players in a score group is odd or there are players who are not pairable within the group for any reason, they will be
"floaters" and will be moved to the next group towards the median. For example, after two rounds, if the number of players with score 1.5 points
will be odd, one player will float to the 1.0 points group and will be paired (if possible) with a partner from that group.
- All matches will be ordered with board numbers bye this rule:
higher player score descending, high player Buchholz descending, higher player serial ascending.
- If the total number of active participants is odd, the lowest-ranked eligible player without a previous bye is selected as bye. Bye is always last board and gets one technical point ("+"), with no color impact or Buchholz for this round.

## How to pair a score group
- These rules apply for a group with score > 50% of the number of past games, for the lower group the rules are reversed.
- Players who already played each other, will not be paired again vs. each others (this is checked by Round.may_be_paired before pairing). This rule is absolute,
so in this case, try to find another possible match within the group, or as last option, float both players to the next group (towards the median) to find other combinations.
- As a first option, the highest player in a group will be paired against the lowest player, second player with second last player and so on.
But this can be exchanged, if they already played, or if their preferred color is the same (this can be checked by multiplying their colorbal -
if it's positive, we'll try to exchange the pairings). For example, with 6 players in a group, the default pairing will be 1 vs. 6, 2 vs. 5 and
3 vs. 4. But if 1 and 6 both positive colorbal and 2 and 5 have both negative colorbal, so we'll match 1-5, 2-6 and 3-4. Color preferences are soft constraints for pairing, except when
both partner have colorbal 3 or both have -3, or their multiple is +9 or more, thus they are not pairable.
- When pairing two players, the one with higher colorbal (than means, played more games as white, or last game as white) will be black. If they're
equal colorbal, the players with higher ranking (higher buchholz or lower serial number) will get their preferred color.
- If the number of players is odd, the lowest ranked will be "floater" to the next group towards the middle (for lower score groups, it will be highest ranged player). For example, after two rounds when pairing
the third, floater from both 1.5 points and 0.5 points will be moved to the 1.0 points group. 
- When floater arrive from both sides of the median, preferable they will not play each other. The floater from upper group will play preferable lowest ranged player in the group, and the floater from lower group will be highest rangd player in the group.
- When greedy pairing block a later player, you can backtrack and rearrange earlier pairings, first within the score group and then outside.
- For floaters, if there is no group at the next half-point toward the median, they will float to the next group towards the median. If they still cannot be paired, they may cross the median.


