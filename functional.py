import itertools
import operator


def csv_reader(file_name):
    for line in open(file_name, "r", encoding="utf8"):
        yield line


def row_splitter(row):
    return row[:-1].split(',')


def generate_rows(file_name):
    csv_gen = csv_reader(file_name)

    columns = row_splitter(next(csv_gen))

    for row in iter(csv_gen):
        yield dict(zip(columns, row_splitter(row)))


def add_to_avg(avg, avg_count, value):
    return (avg * avg_count + value) / (avg_count + 1)


def generate_match_data(row):
    for r in iter(row):
        if r["tournament"] == "FIFA World Cup":
            yield {
                "team_name": r["home_team"],
                "home_goals": int(r["home_score"]),
                "away_goals": int(r["away_score"])
            }
            yield {
                "team_name": r["away_team"],
                "home_goals": int(r["away_score"]),
                "away_goals": int(r["home_score"])
            }


def update_indicator(ind, md):
    matches = ind["wins"] + ind["losses"] + ind["draws"]
    ind["avg_goals_scored"] = add_to_avg(ind["avg_goals_scored"], matches, md["home_goals"])
    ind["avg_goals_taken"] = add_to_avg(ind["avg_goals_taken"], matches, md["away_goals"])

    if md["home_goals"] > md["away_goals"]:
        ind["wins"] += 1
    elif md["home_goals"] < md["away_goals"]:
        ind["losses"] += 1
    else:
        ind["draws"] += 1

    return ind


def generate_indicators(file_name):
    rows = generate_rows(file_name)

    inds = {}
    for match_data in iter(generate_match_data(rows)):
        if inds.get(match_data["team_name"]) is None:
            inds[match_data["team_name"]] = {
                "team_name": match_data["team_name"],
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "avg_goals_scored": 0,
                "avg_goals_taken": 0
            }
        inds[match_data["team_name"]] = update_indicator(inds[match_data["team_name"]], match_data)

    return [el for el in inds.values()]


# {'wins': 0, 'losses': 2, 'draws': 1, 'avg_goals_scored': 0.6666666666666666, 'avg_goals_taken': 1.6666666666666667}
#  indicate(v, mode='or', avg_goals_scored__gt=1, wins__gt=10)
def indicate(ind, **kwargs):
    mode = kwargs.pop('mode', 'or')

    result = False if mode == 'or' else True

    for kw in kwargs:
        if '__' in kw:
            _kw, op = kw.split('__')
            # only allow valid operators
            assert op in ('lt', 'le', 'eq', 'ne', 'ge', 'gt')
        else:
            op = 'eq'
            _kw = kw

        _operator = getattr(operator, op)

        _result = _operator(ind.get(_kw), kwargs[kw])

        if mode == 'or':
            result = _result or result
        else:
            result = _result and result
    return result


def indicator(ind, **kwargs):
    for el in ind:
        if indicate(el, **kwargs):
            yield el


def prettify(ind):
    print("{}, wins: {}, losses: {}, draws: {}, scored goals avg: {}, taken goals avg: {}".format(
        ind["team_name"], ind["wins"], ind["losses"], ind["draws"], ind["avg_goals_scored"], ind["avg_goals_taken"]))


def prettyficator(it):
    for el in iter(it):
        prettify(el)


if __name__ == '__main__':
    indicators = generate_indicators("results.csv")

    S = list(indicator(indicators, team_name__eq="Iceland")).pop()
    prettify(S)

    search_params = {
        "mode": "and",
        "wins__gt": S.get("wins"),
        "avg_goals_scored__gt": S.get("avg_goals_scored")
    }

    more_search_params = {
        "mode": "or",
        "losses__gt": S.get("wins")
    }

    prettyficator(indicator(indicator(ind=indicators, **search_params), **more_search_params))


