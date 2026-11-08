class Player:
    def __init__(self, name, email="", rating=None, serial=None):
        self.serial = None
        self.name = name
        assert rating is None or isinstance(rating, (int, float, str)), (
                f"Rating for {name} in wrong type")
        if type(rating) is str:
            self.rating = float(rating)
        else:
            self.rating = rating
        self.score = 0.0
        self.buchholz = 0.0
        self.percentage = None
        # color balance is the number of games as white,
        # minutes the number of games as black
        self.colorbal = 0
        self.results = []
        self.email = email
        self.opponents = []
        self.games = []
        self.serial = serial
        self.quit = False

    def __gt__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        if hasattr(self, "score") and hasattr(other, "score"):
            if self.score > other.score:
                return True
            elif self.score < other.score:
                return False
            elif self.score == other.score:
                if self.buchholz > other.buchholz:
                    return True
                elif self.buchholz < other.buchholz:
                    return False
                elif self.buchholz == other.buchholz:
                    return self.serial < other.serial

    def __lt__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        if hasattr(self, "score") and hasattr(other, "score"):
            if self.score > other.score:
                return False
            elif self.score < other.score:
                return True
            elif self.score == other.score:
                if self.buchholz > other.buchholz:
                    return False
                elif self.buchholz < other.buchholz:
                    return True
                elif self.buchholz == other.buchholz:
                    return self.serial > other.serial

    def to_dict(self) -> dict:
        return {"name": self.name,
                "serial": self.serial,
                "rating": self.rating,
                "percentage": self.percentage,
                "colorbal": self.colorbal,
                "email": self.email,
                "results": self.results,
                "opponents": self.opponents,
                "score": self.score,
                "games": [],
                "quit": self.quit if hasattr(self, "quit") else False
                }

    def from_dict(self, data: dict):
        self.serial = data.get("serial")
        self.name = data.get("name")
        self.rating = data.get("rating")
        self.score = data.get("score")
        self.buchholz = data.get("bochholz")
        self.percentage = data.get("percentage")
        self.colorbal = data.get("colorbal")
        self.email = data.get("email")
        self.results = data.get("results")
        self.opponents = data.get("opponents")
        self.games = data.get("games")
        #Safety percaution:
        if self.games is None:
            self.games = []
        self.score = data.get("score")
        if self.score is None:
            self.score = 0.0

    def get_rating(self) -> float:
        if isinstance(self.rating, (int, float)):
            return float(self.rating)
        else:
            return 1100.0

    def calculate_score(self):
        self.score = 0.0
        for round_num, game in enumerate(self.games, start=1):
            if game.white == self.serial:
                self.score += game.white_score()
            elif game.black == self.serial:
                self.score += game.black_score()
            else:
                print(f"Data error: player {self.name} not listed",
                      f"in his own round {round_num}")
        print(f"Score for {self.name} is {self.score}")

    def calculate_buchholz(self, all_participants, echo=False):
        self.buchholz = 0
        for _round_num, partner in enumerate(self.opponents):
            if partner != self.serial:
                self.buchholz += all_participants[partner].score
            else:
                self.buchholz += len(self.results)/2
        if echo:
            print(f"Buchholz for {self.name} is {self.buchholz}")
