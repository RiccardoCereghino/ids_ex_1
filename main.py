import operator
import functools
import itertools

def add_to_avg(avg, avg_count, value):
    return (avg * avg_count + value) / (avg_count + 1)


class FootballIndicator:
    def __init__(self, file_name=None, data=None):
        assert (file_name and not data) or (data and not file_name), "initialization error"
        self._data = data if data else {}

        if file_name:
            self.csv_gen = (r for r in open(file_name, "r", encoding="utf8"))
            self.indicate()
            del self.csv_gen

    def __getitem__(self, item: str) -> 'FootballIndicator.TeamIndicator':
        return self._data.get(item)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __iter__(self):
        self.keys = list(self._data.keys())
        return self

    def __next__(self) -> 'FootballIndicator.TeamIndicator':
        if len(self.keys) == 0:
            raise StopIteration
        return self._data[self.keys.pop()]

    def __gt__(self, other):
        pass

    class TeamMatchData:
        def __init__(self, team_name, team_score, opponent_score):
            self.team_name = team_name
            self.team_score = int(team_score)
            self.opponent_score = int(opponent_score)
            self.match_won = True if team_score > opponent_score else False if team_score < opponent_score else None

    class TeamIndicator:
        attributes =\
            ['team', 'wins', 'losses', 'draws', 'avg_goals_scored', 'avg_goals_took', 'number_of_matches', 'score']

        def __init__(self, team_name):
            self.team = team_name
            self.wins = 0
            self.losses = 0
            self.draws = 0
            self.avg_goals_scored = 0
            self.avg_goals_took = 0

        def __dict__(self):
            return {
                "team": self.team,
                "wins": self.wins,
                "losses": self.losses,
                "draws": self.draws,
                "avg_goals_scored": self.avg_goals_scored,
                "avg_goals_took": self.avg_goals_took
            }

        def __str__(self):
            return "TEAM: {}, WINS: {}, LOSSES: {}, DRAWS: {}, AVG_GOALS: {}, AVG_OPPONENT_GOALS: {}".format(
                self.team, self.wins, self.losses, self.draws, self.avg_goals_scored, self.avg_goals_took
            )

        @property
        def number_of_matches(self):
            return self.wins + self.losses + self.draws

        @property
        def score(self):
            return self.wins * 3 - self.losses * 3 + self.draws

        def indicate(self, match_data):
            if match_data.match_won is True:
                self.wins += 1
            elif match_data.match_won is False:
                self.losses += 1
            else:
                self.draws += 1
            self.avg_goals_scored = add_to_avg(self.avg_goals_scored, self.number_of_matches, match_data.team_score)
            self.avg_goals_took = add_to_avg(self.avg_goals_took, self.number_of_matches, match_data.opponent_score)

    @classmethod
    def row_to_python(cls, row):
        return cls.TeamMatchData(team_name=row[1], team_score=row[3], opponent_score=row[4]), \
               cls.TeamMatchData(team_name=row[2], team_score=row[4], opponent_score=row[3])

    def update_data(self, row):
        home_team_dt, away_team_dt = self.row_to_python(row)

        if self[home_team_dt.team_name] is None:
            self[home_team_dt.team_name] = self.TeamIndicator(home_team_dt.team_name)

        self[home_team_dt.team_name].indicate(home_team_dt)

        if self[away_team_dt.team_name] is None:
            self[away_team_dt.team_name] = self.TeamIndicator(away_team_dt.team_name)

        self[away_team_dt.team_name].indicate(away_team_dt)

    def indicate(self):
        next(self.csv_gen)
        for row in self.csv_gen:
            self.update_data(row[:-1].split(','))

    def filter(self, **kwargs):
        # https://stackoverflow.com/a/58349504
        mode = kwargs.pop('mode', 'or')
        result = set()
        for kw in kwargs:
            if '__' in kw:
                _kw, op = kw.split('__')
                # only allow valid operators
                assert op in ('lt', 'le', 'eq', 'ne', 'ge', 'gt')
            else:
                op = 'eq'
                _kw = kw
            _operator = getattr(operator, op)
            # only allow access to valid object attributes
            assert _kw in self.TeamIndicator.attributes

            filtered = (
                obj for obj in self
                if _operator(getattr(obj, _kw), kwargs[kw])
            )
            if mode == 'and':
                if filtered:
                    result = result.intersection(filtered) \
                        if result else set(filtered)
                else:
                    return set()
            else:
                result.update(filtered)

        data = {indicator.team: indicator for indicator in result}
        return FootballIndicator(data=data)


if __name__ == '__main__':
    TEAM = "Iceland"
    football_indicator = FootballIndicator(file_name="results.csv")

    S = football_indicator[TEAM]
    print(S)

    a = football_indicator.filter(mode='and', avg_goals_scored__gt=S.avg_goals_scored).filter(mode='or', draws__lt=S.draws)
    b = a.filter(mode='and', draws__lt=S.draws)
    del a
    c = football_indicator.filter(mode='and', avg_goals_scored__gt=S.avg_goals_scored, wins__gt=S.wins)
    print("as")
