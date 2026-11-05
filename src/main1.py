#!/pkg/qct/software/python/sles12/3.11.4/bin/python3

import tournament
t = tournament.Tournament("Cork site chess 2026", 7)
t.load_players("chess1.csv")
t.sort_players()
t.report_players("all_players.csv")
t.save_data("round0.json")
