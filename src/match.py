import csv
from functools import lru_cache

from player import Player


class Match:
    def __init__(
        self, round_num, white, black, white_result=None, black_result=None, bye=False
    ):
        assert isinstance(round_num, int), "Round number should be an integer"
        assert isinstance(white, int), "White player should have a valid serial number"
        assert isinstance(black, int) or bye, (
            "Black player should have a valid serial number"
        )
        self.round_num = round_num
        self.white = white
        self.bye = bye
        if bye:
            self.black = white
        else:
            self.black = black
        if bye:
            self.white_result = "+"
            self.black_result = None
        else:
            self.white_result = white_result
            self.black_result = black_result

    def update_result(self, white_result, black_result):
        self.white_result = white_result
        self.black_result = black_result

    def white_display_result(self):
        if self.white_result is None:
            return ""
        else:
            return str(self.white_result)

    def white_score(self):
        if self.white_result == 1 or self.white_result == "+" or self.bye:
            return 1.0
        elif self.white_result == 0 or self.white_result == "-":
            return 0.0
        elif self.white_result == 0.5:
            return 0.5

    def black_display_result(self):
        if self.black_result is None:
            return ""
        else:
            return str(self.black_result)

    def black_score(self):
        if self.black_result == 1 or self.black_result == "+" or self.bye:
            return 1
        elif self.black_result == 0 or self.black_result == "-":
            return 0
        elif self.black_result == 0.5:
            return 0.5

    def from_dict(self, data):
        self.round_num = data.get("round_num")
        self.white = data.get("white")
        self.black = data.get("black")
        self.bye = data.get("bye", self.white == self.black)
        self.white_result = data.get("white_result")
        self.black_result = data.get("black_result")

    def to_dict(self):
        return {
                "round_num": self.round_num,
                "white": self.white,
                "black": self.black,
                "white_result": self.white_result,
                "black_result": self.black_result,
                "bye": self.bye,
                }


class Round:
    def __init__(self, round_num):
        self.round_num = round_num
        self.all_matches = []

    def report_games(self, csv_fname=None, tour=None):
        if len(self.all_matches) == 0:
            print(f"No games listed in round {self.round_num} yet")
            return
        print("Round", self.round_num, "matches:")
        print("Board     White         Score       -     Black    Score")
        for board, match in enumerate(self.all_matches, start=1):
            if isinstance(match.white, int):
                white_player = tour.player(match.white)
            else:
                white_player = match.white
            if match.bye:
                black_player = None
            elif isinstance(match.black, int):
                black_player = tour.player(match.black)
            else:
                black_player = match.black
            if match.bye:
                print(
                    f"   {board}   {white_player.name:22}  ",
                    f"{match.white_display_result():5} {'BYE':22}",
                )
            else:
                print(
                    f"   {board}   {white_player.name:22}  ",
                    f"{match.white_display_result():5} {black_player.name:22}",
                    f"  {match.black_display_result():5}",
                )

        if isinstance(csv_fname, str):
            with open(csv_fname, "w", newline="", encoding="utf-8") as csvrep:
                fieldnames = [
                    "Board",
                    "WhiteNum",
                    "WhiteName",
                    "WhiteScore",
                    "BlackNum",
                    "BlackName",
                    "BlackScore",
                ]
                writer = csv.DictWriter(csvrep, fieldnames=fieldnames)
                writer.writeheader()
                for board, match in enumerate(self.all_matches, start=1):
                    if isinstance(match.white, int):
                        white_player = tour.player(match.white)
                    else:
                        white_player = match.white
                    if match.bye:
                        black_player = None
                    elif isinstance(match.black, int):
                        black_player = tour.player(match.black)
                    else:
                        black_player = match.black
                    writer.writerow(
                        {
                            "Board": board,
                            "WhiteNum": white_player.serial,
                            "WhiteName": white_player.name,
                            "WhiteScore": match.white_result,
                            "BlackNum": "" if match.bye else black_player.serial,
                            "BlackName": "" if match.bye else black_player.name,
                            "BlackScore": match.black_result
                        }
                    )

    def import_results(self, csv_fname, tour=None):
        """Import results from a CSV produced by :meth:`report_games`.

        Games must already be paired in ``all_matches``.  Rows are matched to
        games using the one-based ``Board`` column.  Supplying ``tour`` also
        verifies the player serial numbers and names before any results are
        changed.

        Return the number of imported games.
        """
        required_fields = {
            "Board",
            "WhiteNum",
            "WhiteName",
            "WhiteScore",
            "BlackNum",
            "BlackName",
            "BlackScore",
        }

        def parse_result(value, row_num, field):
            value = value.strip()
            if value == "":
                return None
            if value in {"+", "-"}:
                return value
            try:
                result = float(value)
            except ValueError as err:
                raise ValueError(
                    f"CSV row {row_num}: invalid {field} value {value!r}"
                ) from err
            if result not in {0.0, 0.5, 1.0}:
                raise ValueError(
                    f"CSV row {row_num}: invalid {field} value {value!r}"
                )
            return int(result) if result in {0.0, 1.0} else result

        def player_for(player_ref):
            if isinstance(player_ref, int) and tour is not None:
                return tour.player(player_ref)
            return player_ref

        pending_results = []
        seen_boards = set()
        with open(csv_fname, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            fields = set(reader.fieldnames or [])
            missing_fields = required_fields - fields
            if missing_fields:
                missing = ", ".join(sorted(missing_fields))
                raise ValueError(f"CSV is missing required column(s): {missing}")

            for row_num, row in enumerate(reader, start=2):
                try:
                    board = int(row["Board"].strip())
                except (AttributeError, TypeError, ValueError) as err:
                    raise ValueError(
                        f"CSV row {row_num}: Board must be an integer"
                    ) from err
                if board < 1 or board > len(self.all_matches):
                    raise ValueError(
                        f"CSV row {row_num}: board {board} is not in this round"
                    )
                if board in seen_boards:
                    raise ValueError(f"CSV row {row_num}: duplicate board {board}")
                seen_boards.add(board)

                match = self.all_matches[board - 1]
                if tour is not None:
                    white_player = player_for(match.white)
                    expected = {
                        "WhiteNum": str(white_player.serial),
                        "WhiteName": white_player.name,
                    }
                    if match.bye:
                        expected.update({"BlackNum": "", "BlackName": ""})
                    else:
                        black_player = player_for(match.black)
                        expected.update({
                            "BlackNum": str(black_player.serial),
                            "BlackName": black_player.name,
                        })
                    for field, expected_value in expected.items():
                        actual_value = row[field].strip()
                        if actual_value != expected_value:
                            raise ValueError(
                                f"CSV row {row_num}: {field} is {actual_value!r}; "
                                f"expected {expected_value!r} for board {board}"
                            )

                white_result = parse_result(
                    row["WhiteScore"], row_num, "WhiteScore"
                )
                black_result = parse_result(
                    row["BlackScore"], row_num, "BlackScore"
                )
                pending_results.append((match, white_result, black_result))

        for match, white_result, black_result in pending_results:
            match.update_result(white_result, black_result)
        if (
            tour is not None and
            len(seen_boards) == len(self.all_matches) and
            hasattr(tour, "last_round_played")
        ):
            tour.last_round_played = max(
                tour.last_round_played, self.round_num
            )
        return len(pending_results)

    def to_dict(self) -> dict:
        return {
            "round_num": self.round_num,
            "all_matches": [a_match.to_dict() for a_match in self.all_matches],
        }

    def from_dict(self, data: dict, tour=None):
        self.round_num = data.get("round_num")
        all_matches = data.get("all_matches")
        print(f"Importing {len(all_matches)} matches from round {self.round_num}")
        self.all_matches = []
        for a_match in all_matches:
            new_match = Match.__new__(Match)
            new_match.from_dict(a_match)
            self.all_matches.append(new_match)
            if tour:
                tour.player(new_match.white).games.append(new_match)
                if not new_match.bye:
                    tour.player(new_match.black).games.append(new_match)

    def may_be_paired(self, white, black, tour=None):
        if isinstance(white, Player):
            white_player = white
            white_number = white.serial
        elif isinstance(white, int) and tour:
            white_player = tour.player(white)
            white_number = white
        else:
            print("No tournament data to extract from!")
            return False
        white_opponent_numbers = white_player.opponents
        if isinstance(black, Player):
            black_player = black
            black_number = black.serial
        elif isinstance(black, int) and tour:
            black_player = tour.player(black)
            black_number = black
        black_opponent_numbers = black_player.opponents
        if (
            black_number in white_opponent_numbers
            or white_number in black_opponent_numbers
        ):
            return False
        else:
            return True

    def pair_players(self, round_num, white, black, bye=False, tour=None):
        if self.may_be_paired(white, black, tour) or bye:
            new_match = Match(round_num, white, black, bye=bye)
            self.all_matches.append(new_match)
            white_player = tour.player(white)
            assert isinstance(white_player, Player), f"Player {white} is not valid"
            white_player.games.append(new_match)
            if not bye:
                black_player = tour.player(black)
                assert isinstance(black_player, Player), (
                    f"Player {black} is not valid"
                )
                white_player.opponents.append(black)
                black_player.opponents.append(white)
                black_player.games.append(new_match)
        else:
            raise ValueError(f"Players {white} and {black} cannot be matched")

    def pair_first_round(self, tour):
        active = [
            player.serial for player in tour.all_participants
            if not getattr(player, "quit", False)
        ]
        part_num = len(active)
        half_part = part_num // 2
        for index in range(half_part):
            upper = active[index]
            lower = active[index + half_part]
            if index % 2 == 1:
                self.pair_players(1, upper, lower, tour=tour)
            else:
                self.pair_players(1, lower, upper, tour=tour)
        if part_num % 2 == 1:
            self.pair_players(1, active[-1], None, bye=True, tour=tour)
        print("Pairing complete")
        tour.last_round_paired = 1

    @staticmethod
    def _rank_key(player):
        """Return the documented standings order (lower tuple is better)."""
        return (-player.score, -player.buchholz, player.serial)

    def _assign_colors(self, first, second):
        """Return ``(white, black)`` serials using color balance preferences."""
        if first.colorbal > second.colorbal:
            return second.serial, first.serial
        if second.colorbal > first.colorbal:
            return first.serial, second.serial

        higher, lower = sorted((first, second), key=self._rank_key)
        if higher.colorbal > 0:
            return lower.serial, higher.serial
        if higher.colorbal < 0:
            return higher.serial, lower.serial
        return higher.serial, lower.serial

    @staticmethod
    def _pair_allowed(first, second):
        if second.serial in first.opponents or first.serial in second.opponents:
            return False
        return first.colorbal * second.colorbal < 9

    def _pair_later_round(self, round_num, tour):
        tour.update_players_data(for_pairing=True)
        active = [
            player for player in tour.all_participants
            if not getattr(player, "quit", False)
        ]
        if not active:
            raise ValueError("At least one active player is required")

        bye_player = None
        if len(active) % 2:
            previous_byes = {
                match.white
                for a_round in tour.all_rounds
                for match in a_round.all_matches
                if match.bye
            }
            eligible = [
                player for player in active
                if player.serial not in previous_byes
            ]
            if not eligible:
                raise ValueError("No active player is eligible for a bye")
            bye_player = max(eligible, key=self._rank_key)
            active.remove(bye_player)

        score_groups = {}
        for player in sorted(active, key=self._rank_key):
            score_groups.setdefault(player.score, []).append(player)
        median_score = (round_num - 1) / 2
        upper_scores = sorted(
            (score for score in score_groups if score > median_score),
            reverse=True,
        )
        lower_scores = sorted(
            score for score in score_groups if score < median_score
        )
        pairing_scores = upper_scores + lower_scores
        if median_score in score_groups:
            pairing_scores.append(median_score)

        active = []
        for score in pairing_scores:
            group = score_groups[score]
            if score < median_score:
                active.extend(reversed(group))
            else:
                active.extend(group)
        group_positions = {
            player.serial: index
            for group in score_groups.values()
            for index, player in enumerate(group)
        }

        def pair_cost(first, second, white_num, black_num):
            score_gap = int(round(abs(first.score - second.score) * 2))
            crosses_median = int(
                (first.score - median_score) *
                (second.score - median_score) < 0
            )
            float_penalty = 0
            if first.score != second.score:
                higher_score = first if first.score > second.score else second
                lower_score = second if higher_score is first else first
                if higher_score.score > median_score:
                    position = group_positions[higher_score.serial]
                    float_penalty += (
                        len(score_groups[higher_score.score]) - 1 - position
                    )
                    destination_position = group_positions[lower_score.serial]
                    float_penalty += (
                        len(score_groups[lower_score.score]) - 1 -
                        destination_position
                    )
                if lower_score.score < median_score:
                    float_penalty += group_positions[lower_score.serial]
                    float_penalty += group_positions[higher_score.serial]

            same_preference = int(first.colorbal * second.colorbal > 0)
            white = tour.player(white_num)
            black = tour.player(black_num)
            resulting_imbalance = int(round(2 * (
                abs(white.colorbal + 1) + abs(black.colorbal - 1)
            )))
            default_penalty = 0
            if first.score == second.score:
                group_size = len(score_groups[first.score])
                expected_sum = group_size - 1
                if group_size % 2:
                    if first.score < median_score:
                        expected_sum += 1
                    else:
                        expected_sum -= 1
                actual_sum = (
                    group_positions[first.serial] +
                    group_positions[second.serial]
                )
                default_penalty = abs(actual_sum - expected_sum)
            return (
                score_gap,
                crosses_median,
                float_penalty,
                same_preference,
                resulting_imbalance,
                default_penalty,
            )

        @lru_cache(maxsize=None)
        def solve(mask):
            if mask == 0:
                return ()

            first_index = (mask & -mask).bit_length() - 1
            first = active[first_index]
            remaining = mask & ~(1 << first_index)
            candidates = []
            candidate_mask = remaining
            while candidate_mask:
                second_bit = candidate_mask & -candidate_mask
                second_index = second_bit.bit_length() - 1
                candidate_mask &= ~second_bit
                second = active[second_index]
                if not self._pair_allowed(first, second):
                    continue

                white_num, black_num = self._assign_colors(first, second)
                local = pair_cost(first, second, white_num, black_num)
                candidates.append(
                    (local, white_num, black_num, second_bit)
                )
            candidates.sort(
                key=lambda candidate: (
                    candidate[0], candidate[1], candidate[2]
                )
            )
            for _cost, white_num, black_num, second_bit in candidates:
                sub_pairs = solve(remaining & ~second_bit)
                if sub_pairs is not None:
                    return ((white_num, black_num),) + sub_pairs
            return None

        solution = solve((1 << len(active)) - 1)
        if solution is None:
            raise ValueError(
                "Unable to pair every active player without a rematch or "
                "a prohibited color conflict"
            )

        serial_pairs = solution
        matches = [
            Match(round_num, white_num, black_num)
            for white_num, black_num in serial_pairs
        ]

        def board_key(match):
            first = tour.player(match.white)
            second = tour.player(match.black)
            upper = min((first, second), key=self._rank_key)
            return self._rank_key(upper)

        matches.sort(key=board_key)
        if bye_player is not None:
            matches.append(
                Match(round_num, bye_player.serial, None, bye=True)
            )

        self.all_matches = matches
        tour.last_round_paired = round_num
        print("Pairing complete")

    def pair(self, round_num, tour):
        if round_num == 1:
            print("Pairing first round...")
            self.pair_first_round(tour)
        else:
            print(f"Pairing round {round_num}...")
            self._pair_later_round(round_num, tour)
