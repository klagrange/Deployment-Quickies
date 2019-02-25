"""Define common functions needed
"""
import math
from scipy import special
#from scipy.stats import norm

def calculate_pv(amount, time, rate):
    """Calculates the present value of an accumulated
    `amount` over a certain `time` (number of years) at a
    compounded interest of `rate`.

    Args:
        amount (float):
        time (int):
        rate (float):

    Returns:
        present value (float)
    """
    return amount / (1 + rate) ** time


def calculate_fv(present_value, time, rate):
    """
    calculate the future value of present_value over a certain 'time' at
    a compound interest of 'rate'
    """
    return present_value* ((1 + rate) ** time)

def calculate_probability(goal, future_v, rate, numberof_days, sigma):
    """
    calculate the probability to achieve a value of "goal"
    future_value: the actual investigated value
    """
    a_fa = -(goal / future_v - (1 + rate) ** (numberof_days / 252)) * math.sqrt(252 / numberof_days) / sigma
    prob = special.ndtr(a_fa)
    return prob

def probability_of_goals(
        goals,
        years,
        ir_per_goal,
        sigma,
        goals_list,
        surplus_list):

    """
    summarize probabilities to achieve each goal
    """
    number_of_goals = len(goals)
    probs_list = []
    for j in range(number_of_goals):
        fv_temp = 0
        numberof_days = (years[j]-1) * 252
        for i in range(int(years[j])):
            fv_temp += calculate_fv(goals_list[j][i][1],\
                                years[j] - i - 1, ir_per_goal[j])
        temp1 = calculate_probability(
            goals[j],
            fv_temp,
            ir_per_goal[j],
            numberof_days,
            sigma[j])
        probs_list.append(round(temp1, 6))
    return probs_list

def calculate_ir(future_v, present_v, year):
    """
    calculate rate based on the "present_v" and "future_v"
    for a given time "year"
    """
    rate = math.pow(future_v / present_v, 1 / year) - 1
    return rate


def input_priority():
    """
    to allow to select investment strategy:  number of 1 ~ 6
    """
    get_input = input("""
        1: AI-equalweighted;
        2: AI-priorityweighted;
        3: II_AI_equalweighted;
        4: II_AI_priorityweighted;
        5: II_equalweighted, AI_priorityweighted;
        6: II_priorityweighted, AI_equalweighted
    please select strategy: """)
    return int(get_input)


def input_adjustment():
    """
    to allow to select adjustment strategy:  number of 1 ~ 6
    """
    get_adjustment = input("""
        1: Adjusting target amounts for goals
        2: Adjusting target years for goals
        3: Adjusting IR to remove shortfall
        4: Adjusting annual_investment
        5: Adjusting initial_investment
        6: Adjusting goal priority
    please select adjustment method: """)
    return int(get_adjustment)
