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
        if bye:
            self.black = white
        else:
            self.black = black
        if bye:
            self.white_result = 0.5
            self.black_result = 0.5
        else:
            self.white_result = None
            self.black_result = None

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
            return 1
        elif self.white_result == 0 or self.white_result == "-":
            return 0
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
        set.black = data.get("black")
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
                white_player = tour.all_participants[match.white]
            else:
                white_player = match.white
            if isinstance(match.black, int):
                black_player = tour.all_participants[match.black]
            else:
                black_player = match.black
            print(
                f"   {board}   {white_player.name:22}  ",
                f"{match.white_display_result():5} {black_player.name:22}",
                f"  {match.black_display_result():5}",
            )

        if isinstance(csv_fname, str):
            with open(csv_fname, "w") as csvrep:
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
                for board, match in enumerate(self.matches, start=1):
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

    def to_dict(self) -> dict:
        return {
            "round_num": self.round_num,
            "all_matches": [a_match.to_dict() for a_match in self.all_matches],
        }

    def from_dict(self, data: dict, tour=None):
        self.round_num = data.get("round_num")
        all_matches = data.get("all_matches")
        print(f"Importing {len(all_matches)} matches from round {self.round_num}")
        for a_match in all_matches:
            new_match = Match.__new__(Match)
            new_match.from_dict(a_match)
            self.all_matches.append(new_match)
            if tour:
                tour.all_participants[new_match.white].games.append(new_match)
                if new_match.white != new_match.black:
                    tour.all_participants[new_match.black].games.append(new_match)

    def may_be_paired(self, white, black, tour=None):
        if isinstance(white, Player):
            white_player = white
            white_number = white.serial
        elif isinstance(white, int) and tour:
            white_player = tour.all_participants[white]
            white_number = white
        else:
            print("No tournament data to extract from!")
            return False
        white_opponent_numbers = [
            opponent.serial for opponent in white_player.opponents
        ]
        if isinstance(black, Player):
            black_player = black
            black_number = black.serial
        elif isinstance(black, int) and tour:
            black_player = tour.all_participants[black]
            black_number = black
        black_opponent_numbers = [
            opponent.serial for opponent in black_player.opponents
        ]
        if (
            black_number in white_opponent_numbers
            or white_number in black_opponent_numbers
        ):
            return False
        else:
            return True

    def pair_players(self, round_num, white, black, bye=False, tour=None):
        if self.may_be_paired(white, black, tour) or bye:
            new_match = Match(round_num, white, black, bye)
            self.all_matches.append(new_match)
            white_player = tour.all_participants[white]
            black_player = tour.all_participants[black]
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
        for i in range(0, half_part):
            if i % 2 == 1:
                self.pair_players(1, i, i + half_part, tour=tour)
            else:
                self.pair_players(1, i + half_part, i, tour=tour)
        if part_num % 2 == 1:
            self.pair_players(
                1, part_num - 1, part_num - 1, bye=True, tour=tour
            )
        print("Pairing complete")
        tour.last_round_paired = 1

    def pair(self, round_num, tour):
        if round_num == 1:
            print("Pairing first round...")
            self.pair_first_round(tour)
        else:
            print("Not supported yet")
