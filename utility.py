def ao_to_do(odds):
    """converts american odds to decimal odds"""
    if odds > 0:
        return (odds+100)/100
    else:
        return (abs(odds) + 100)/abs(odds)


def do_to_ao(odds):
    """converts decimal odds to american odds"""
    if odds >= 2:
        return 100 * (odds-1)
    else:
        return -100/(odds-1)


def get_break_even(odds):
    """takes decimal_odds and returns break-even percentage"""
    return 1 / odds


def get_over_round(be1, be2):
    """takes two break-even probabilities and calculates the over-round"""
    over_round = (be1 + be2) - 1
    return over_round


def get_vig(over_round):
    """Takes the over_round and calculates the vig"""
    vig = over_round/(1 + over_round)
    return vig

