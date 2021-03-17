import operator
from itertools import tee


def add_to_avg(avg, avg_count, value):
    return (avg * avg_count + value) / (avg_count + 1)


def row_splitter(row):
    return row[:-1].split(',')


def csv_reader(file_name):
    for line in open(file_name, "r", encoding="utf8"):
        yield line


def generate_rows(file_name):
    csv_gen = csv_reader(file_name)

    columns = row_splitter(next(csv_gen))

    for row in csv_gen:
        yield dict(zip(columns, row_splitter(row)))


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
        ind["win_streaks"][-1] += 1
    else:
        if md["home_goals"] < md["away_goals"]:
            ind["losses"] += 1
        else:
            ind["draws"] += 1
        if ind["win_streaks"][-1] != 0:
            ind["win_streaks"].append(0)
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
                "avg_goals_taken": 0,
                "win_streaks": [0]
            }
        inds[match_data["team_name"]] = update_indicator(inds[match_data["team_name"]], match_data)

    for el in inds.values():
        el["max_win_streak"] = max(el.pop("win_streaks"))
        yield el


def selector(ind, mode, operators):

    result = False if mode == 'or' else True

    for operation in operators:
        _result = operation(ind)

        if mode == 'or':
            result = _result or result
        else:
            result = _result and result
    return result


def operators_reader(**kwargs):
    operators = []
    for kw in kwargs:
        if '__' in kw:
            _kw, op = kw.split('__')
            # only allow valid operators
            assert op in ('lt', 'le', 'eq', 'ne', 'ge', 'gt')
        else:
            op = 'eq'
            _kw = kw

        _operator = getattr(operator, op)

        operators.append(lambda x: _operator(x.get(_kw), kwargs[kw]))

    return operators


def select(ind, **kwargs):
    """
    It is possible to concatenate select as it returns generators
    select(select(ind=ind_2, **search_params), **more_search_params)

    :param ind: generator
    :param kwargs
    :return: generator
    """
    mode = kwargs.pop('mode', 'or')
    operators = operators_reader(**kwargs)
    return filter(lambda el: selector(el, mode, operators), ind)


def prettify(ind):
    print(
        "{}, wins: {}, losses: {}, draws: {}, scored goals avg: {}, taken goals avg: {}, max_win_streak: {}".format(
            ind["team_name"], ind["wins"], ind["losses"], ind["draws"], ind["avg_goals_scored"],
            ind["avg_goals_taken"], ind["max_win_streak"]
        )
    )


def prettyficator(it):
    for el in iter(it):
        prettify(el)


if __name__ == '__main__':
    indicators = generate_indicators("results.csv")
    ind_1, ind_2 = tee(indicators, 2)

    print("Iceland indicators")
    S = list(select(ind_1, team_name__eq="Iceland")).pop()
    prettify(S)

    search_params = {
        "mode": "and",
        "wins__gt": S.get("wins"),
        "losses__lt": S.get("losses"),
        "avg_goals_scored__gt": S.get("avg_goals_scored"),
        "avg_goals_taken__lt": S.get("avg_goals_taken"),
        "max_win_streak__gt": S.get("max_win_streak")
    }

    print("Teams with indicators better than Iceland")
    prettyficator(select(ind=ind_2, **search_params))
