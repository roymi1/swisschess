import csv
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
            self.white_result = 0.5
            self.black_result = 0.5
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
        self.bye = self.white == self.black
        self.white_result = data.get("white_result")
        self.black_result = data.get("black_result")

    def to_dict(self):
        return {
                "round_num": self.round_num,
                "white": self.white,
                "black": self.black,
                "white_result": self.white_result,
                "black_result": self.black_result
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
            if isinstance(match.black, int):
                black_player = tour.player(match.black)
            else:
                black_player = match.black
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
                    if isinstance(match.black, int):
                        black_player = tour.player(match.black)
                    else:
                        black_player = match.black
                    writer.writerow(
                        {
                            "Board": board,
                            "WhiteNum": white_player.serial,
                            "WhiteName": white_player.name,
                            "WhiteScore": match.white_result,
                            "BlackNum": black_player.serial,
                            "BlackName": black_player.name,
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
                return tour.all_participants[player_ref]
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
                    black_player = player_for(match.black)
                    expected = {
                        "WhiteNum": str(white_player.serial),
                        "WhiteName": white_player.name,
                        "BlackNum": str(black_player.serial),
                        "BlackName": black_player.name,
                    }
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
                if new_match.black:
                    tour.player(new_match.black).games.append(new_match)

    def may_be_paired(self, white, black, tour=None):
        if isinstance(white, Player):
            white_player = white
            white_number = white.serial
        elif isinstance(white, int) and tour:
            white_player = tour.player(white)
            white_number = tour.player(black)
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
            black_player = tour.player(black)
            assert isinstance(white_player, Player), f"Player {white} is not valid"
            assert isinstance(black_player, Player), f"Player {black} is not valid"
            white_player.opponents.append(black)
            white_player.games.append(new_match)
            if not bye:
                black_player.opponents.append(white)
                black_player.games.append(new_match)
        else:
            print(f"Error: {white.name} and {black.name} cannot be matched!")
            raise ValueError(f"Error: {white.name} and {black.name} cannot be matched!")

    def pair_first_round(self, tour):
        part_num = len(tour.all_participants)
        half_part = part_num // 2
        for i in range(1, half_part+1):
            if i % 2 == 0:
                self.pair_players(1, i, i + half_part, tour=tour)
            else:
                self.pair_players(1, i + half_part, i, tour=tour)
        if part_num % 2 == 1:
            self.pair_players(
                1, part_num - 1, None, bye=True, tour=tour
            )
        print("Pairing complete")
        tour.last_round_paired = 1

    def pair(self, round_num, tour):
        if round_num == 1:
            print("Pairing first round...")
            self.pair_first_round(tour)
        else:
            print("Not supported yet")
