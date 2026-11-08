from player import Player
from match import Round
import csv
import os
import json


class Tournament:
    def __init__(self, tournament_name, rounds_num):
        self.name = tournament_name
        self.rounds_num = rounds_num
        self.all_participants = []
        self.all_rounds = []
        self.last_round_paired = 0
        self.last_round_played = 0

    def player(self, serial):
        if not isinstance(serial, int) or serial < 1:
            raise ValueError(f"Invalid player serial: {serial}")
        return self.all_participants[serial - 1]

    def round(self, round_num):
        if not isinstance(round_num, int) or round_num < 1:
            raise ValueError(f"Invalid round number: {round_num}")
        return self.all_rounds[round_num - 1]

    def load_players(self, csv_fname, keep_serial=False):
        # Load list of participants from CSV file
        with open(csv_fname) as csvfile:
            csvfile.readline()
            csvfile.readline()
            participant_reader = csv.reader(csvfile)
            for row in participant_reader:
                print("Parsing row:", row)
                try:
                    serial = row[0]
                    name = row[1]
                    email = row[2]
                    if len(row) > 3:
                        rating = row[3]
                        rating = rating.replace("~", "").replace("?", "")
                    print("Read participant:", name)
                except Exception as err:
                    print("Unable to parse line:", err)
                    continue
                if rating.strip().isnumeric():
                    rating = float(rating)
                else:
                    rating = None
                if not keep_serial:
                    serial = None
                self.all_participants.append(Player(name, email=email, rating=rating,
                                                    serial=serial))
            print("Total of", len(self.all_participants), "imported")

    def sort_players(self):
        def rating(p: Player) -> float:
            return p.get_rating()

        self.all_participants.sort(reverse=True, key=rating)
        for i, participant in enumerate(self.all_participants, start=1):
            participant.serial = i

    def report_players(self, csv_fname=None):
        def disp(rating) -> str:
            if rating is None:
                return "      "
            else:
                return f"{rating:4.1f}"

        print("     Serial      Name                   ",
              "E-mail              Rating           Score")
        for part in self.all_participants:
            print(f"     {part.serial:3d}       {part.name:20s}    ",
                  f" {part.email:25}      {disp(part.rating)}     ",
                  f"{part.score:2.1f}   ")
        print()
        if isinstance(csv_fname, str):
            with open("participants_list.csv", "w") as csvrep:
                fieldnames = ['Serial', 'Name', 'Email', 'Rating']
                writer = csv.DictWriter(csvrep, fieldnames=fieldnames)
                writer.writeheader()
                for a_player in self.all_participants:
                    writer.writerow({'Serial': a_player.serial,
                                     'Name': a_player.name,
                                     'Email': a_player.email,
                                     'Rating': a_player.rating
                                     })

    def to_dict(self):
        return {
                "name": self.name,
                "rounds_num": self.rounds_num,
                "last_round_paired": self.last_round_paired,
                "last_round_played": self.last_round_played,
                "all_participants": [a_player.to_dict() for
                                     a_player in self.all_participants],
                "all_rounds": [a_round.to_dict() for a_round
                               in self.all_rounds]
                }

    def from_dict(self, data):
        self.name = data.get("name")
        self.rounds_num = data.get("rounds_num")
        self.last_round_played = data.get("last_round_played")
        self.last_round_paired = data.get("last_round_paired")
        self.all_participants = []
        self.all_rounds = []
        for parts in data.get("all_participants"):
            new_player = Player.__new__(Player)
            new_player.from_dict(parts)
            self.all_participants.append(new_player)
        for rounds in data.get("all_rounds"):
            new_round = Round.__new__(Round)
            new_round.from_dict(rounds, self)
            self.all_rounds.append(new_round)

    def save_data(self, fname=None):
        if not fname:
            if os.path.exists("chess1.old5.json"):
                os.remove("chess1.old5.json")
            if os.path.exists("chess1.old4.json"):
                os.rename("chess1.old4.json", "chess1.old5.json")
            if os.path.exists("chess1.old3.json"):
                os.rename("chess.old3.json", "chess1.old4.json")
            if os.path.exists("chess1.old2.json"):
                os.rename("chess1.old2.json", "chess1.old3.json")
            if os.path.exists("chess1.old1.json"):
                os.rename("chess1.old1.json", "chess1.old2.json")
            if os.path.exists("chess1.old.json"):
                os.rename("chess1.json", "chess1.old1.json")
            with open("chess1.json", "w") as json_data:
                t_data = self.to_dict()
            print("Data saved to chess1.json")
        else:
            with open(fname, "w") as json_data:
                t_data = self.to_dict()
                json.dump(t_data, json_data, indent=4)
            print("Data saved to", fname)

    def load_data(self, file):
        try:
            if isinstance(file, str) and os.path.exists(file):
                print("Reading data from", file)
            else:
                file = "chess1.json"
                print("Reading data from", file)
            data_f = open(file)
            data = json.load(data_f)
            if len(data) > 2:
                print("Sucessfully read data for", data.get("name"))
                self.from_dict(data)
        except Exception as err:
            print("Unable to read tournament data from", file, ":\n", err)

    def update_players_data(self, for_pairing=False):
        """Rebuild player statistics from the tournament's matches.

        When ``for_pairing`` is true, a missing game result counts as 0.5 for
        each player, as required by the pairing rules.  Games, results and
        opponents are derived data and are rebuilt here to avoid stale or
        duplicated entries.
        """
        for player in self.all_participants:
            player.score = 0.0
            player.buchholz = 0.0
            player.colorbal = 0.0
            player.results = []
            player.opponents = []
            player.games = []

        last_was_bye = {player.serial: False for player in self.all_participants}
        last_color = {player.serial: None for player in self.all_participants}

        for a_round in self.all_rounds:
            for match in a_round.all_matches:
                white_player = self.player(match.white)
                white_player.games.append(match)
                if match.bye:
                    white_player.score += 1.0
                    white_player.results.append("+")
                    last_was_bye[white_player.serial] = True
                    continue

                black_player = self.player(match.black)
                black_player.games.append(match)
                white_player.opponents.append(black_player.serial)
                black_player.opponents.append(white_player.serial)
                white_player.results.append(match.white_result)
                black_player.results.append(match.black_result)

                white_score = match.white_score()
                black_score = match.black_score()
                if for_pairing:
                    if white_score is None:
                        white_score = 0.5
                    if black_score is None:
                        black_score = 0.5
                white_player.score += white_score or 0.0
                black_player.score += black_score or 0.0

                white_player.colorbal += 1.0
                black_player.colorbal -= 1.0
                last_color[white_player.serial] = "white"
                last_color[black_player.serial] = "black"
                last_was_bye[white_player.serial] = False
                last_was_bye[black_player.serial] = False

        for player in self.all_participants:
            player.buchholz = sum(
                self.player(opponent).score for opponent in player.opponents
            )
            if player.colorbal == 0 and not last_was_bye[player.serial]:
                if last_color[player.serial] == "white":
                    player.colorbal = 0.5
                elif last_color[player.serial] == "black":
                    player.colorbal = -0.5

    def report_standings(self, csv_fname=None):
        def disp(rating) -> str:
            if rating is None:
                return "      "
            else:
                return f"{rating:4.1f}"

        self.update_players_data()
        players_sorted = self.all_participants.copy()
        players_sorted.sort(reverse=True)

        print("     Serial      Name                   ",
              "E-mail              Rating           Score Buchholz")
        for part in players_sorted:
            print(f"     {part.serial:3d}       {part.name:20s}    ",
                  f" {part.email:25}      {disp(part.rating)}     ",
                  f"{part.score:2.1f}  {part.buchholz:2.1f} ")
        print()
        if isinstance(csv_fname, str):
            with open("participants_list.csv", "w") as csvrep:
                fieldnames = ['Serial', 'Name', 'Email', 'Rating']
                writer = csv.DictWriter(csvrep, fieldnames=fieldnames)
                writer.writeheader()
                for a_player in self.all_participants:
                    writer.writerow({'Serial': a_player.serial,
                                     'Name': a_player.name,
                                     'Email': a_player.email,
                                     'Rating': a_player.rating
                                     })

    def pair_round(self, new_round=None):
        if isinstance(new_round, int):
            if new_round == self.last_round_played + 1:
                if new_round == self.last_round_paired + 1:
                    newly_round = Round(new_round)
                    newly_round.pair(new_round, self)
                    if self.last_round_paired > self.last_round_played:
                        self.all_rounds.append(newly_round)
                elif new_round == self.last_round_paired:
                    confirm = input(
                        f"Round number {new_round} already paired - overwrite?")
                    if confirm.lower.startswith("y"):
                        newly_round = Round(new_round)
                        newly_round.pair(new_round, self)
                    else:
                        print("Keeping previous pairing for round", new_round)
            else:
                print("Some is wrong - last round played is", self.last_round_played)
                return
        elif new_round is None:
            if self.last_round_paired == self.last_round_played:
                new_round = self.last_round_played + 1
                newly_round = Round(new_round)
                newly_round.pair(new_round, self)
                if self.last_round_paired > self.last_round_played:
                    self.all_rounds.append(newly_round)
            else:
                print(f"Something is wrong - paired round {self.last_round_paired}",
                      f"but has only results for {self.last_round_played}",
                      "Complete missing results first!")
                return
