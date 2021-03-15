from enum import Enum
import pandas as pd


class FootballResults:
    def __init__(self, file_name):
        self.csv_gen = (r for r in open(file_name, "r", encoding="utf8"))
        self.data = {}

    class TeamMatchData:
        def __init__(self, team_name, team_score, opponent_score):
            self.team_name = team_name
            self.team_score = int(team_score)
            self.opponent_score = int(opponent_score)
            self.match_won = True if team_score > opponent_score else False if team_score < opponent_score else None

    class TeamIndicator:
        def __init__(self, team_name):
            self.team = team_name
            self.wins = 0
            self.losses = 0
            self.draws = 0
            self.goals_scored = 0
            self.goals_took = 0
            self.avg_goals_scored = 0
            self.avg_goals_took = 0

        def __dict__(self):
            return {
                "team": self.team,
                "wins": self.wins,
                "losses": self.losses,
                "draws": self.draws,
                "goals_scored": self.goals_scored,
                "goals_took": self.goals_took,
                "avg_goals_scored": self.avg_goals_scored,
                "avg_goals_took": self.avg_goals_took
            }

        def indicate(self, match_data):
            if match_data.match_won is True:
                self.wins += 1
            elif match_data.match_won is False:
                self.losses += 1
            else:
                self.draws += 1
            self.goals_scored += match_data.team_score
            self.goals_took += match_data.opponent_score

        def finalize(self):
            matches = self.wins + self.losses + self.draws
            self.avg_goals_scored = self.goals_scored / matches
            self.avg_goals_took = self.goals_took / matches

    @classmethod
    def row_to_python(cls, row):
        return cls.TeamMatchData(team_name=row[1], team_score=row[3], opponent_score=row[4]), \
               cls.TeamMatchData(team_name=row[2], team_score=row[4], opponent_score=row[3])

    def update_data(self, row):
        home_team_dt, away_team_dt = self.row_to_python(row)

        if not self.data.get(home_team_dt.team_name):
            self.data[home_team_dt.team_name] = self.TeamIndicator(home_team_dt.team_name)
        self.data.get(home_team_dt.team_name).indicate(home_team_dt)

        if not self.data.get(away_team_dt.team_name):
            self.data[away_team_dt.team_name] = self.TeamIndicator(away_team_dt.team_name)
        self.data.get(away_team_dt.team_name).indicate(away_team_dt)

    def indicate(self):
        next(self.csv_gen)
        for row in self.csv_gen:
            self.update_data(row[:-1].split(','))
        for k, v in self.data.items():
            v.finalize()
        return self.data


if __name__ == '__main__':
    # print(df[df["country"] == "Iceland"])
    # self.pd_read = pd.read_csv(file_name)

    TEAM = "Iceland"
    a = FootballResults(file_name="results.csv").indicate()
    print(a[TEAM].__dict__())
