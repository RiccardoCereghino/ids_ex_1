from enum import Enum
import pandas as pd


class MatchResult(Enum):
    DRAW = 0
    HOME_WIN = 1
    AWAY_WIN = 2


class FootballResults:
    TEAM = "Iceland"

    def __init__(self, file_name):
        self.csv_gen = (r for r in open(file_name, "r", encoding="utf8"))
        # print(df[df["country"] == "Iceland"])

        self.pd_read = pd.read_csv(file_name)

    @staticmethod
    def row_to_python(row):
        date = row[0], home_team = row[1], away_team = row[2], home_score = row[3], away_score = row[4]
        match_result = \
            MatchResult(1) if home_score > away_score else MatchResult(2) if home_score < away_score else MatchResult(0)
        return date, match_result, home_team, home_score, away_team, away_score

    def indicate(row):
        # return reduce((lambda x, y: x + y), csv_gen)
        pass

    def __iter__(self):
        self.num = 1
        return self

    def __next__(self):
        num = self.num
        self.num += 2
        return num


"""
    for row in csv_gen:
        row = row[:-1].split(',')
        indicate(row)

"""

"""
it = indicator(team)
for row in csv_gen:
    it(row[:-1].split(','))


def indicator(team):
    wins = losses = draws = pos_score = neg_score = 0
    for row in csv_gen:
        it(row[:-1].split(','))



def counter(maximum):
    print("CCC")
    i = 0
    while i < maximum:
        print("DDD")
        val = (yield i)
        print("AA: {}".format(val))
        if val is not None:
            i = val
        else:
            i += 1

it = counter(10)

print(it.send(None))
print("BBB")
print(it.send(6))
print(next(it))
print(it.__next__())


class InfIter:
    Infinite iterator to return all
        odd numbers

    def __iter__(self):
        self.num = 1
        return self

    def __next__(self):
        num = self.num
        self.num += 2
        return num

a = iter(InfIter())
print(next(a))
print(next(a))

def indicator(df, country: str):
    wins = losses = draws = pos_score = neg_score = None
    for row in df:
        if row['country'] == country:
            continue

    return (wins, losses, draws, pos_score, neg_score)

def country_list(country_cloumn):
    return country_cloumn

def country_filter(countries: list, country: str):
    return countries[country] == countr
"""

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = iter(FootballResults(file_name="results.csv"))
    print(next(a))
    print(next(a))
    print(next(a))
