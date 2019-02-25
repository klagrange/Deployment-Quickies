#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 13:46:33 2018
This contains functions to calcuate cash flow year by year
@author: liujin
"""
import math
import numpy as np
import helpers as hp
import post_processor as pp
# here is the main function to process cash flow

def calculator_ai_equal(goals, years, annual_investment, ir_per_goal, frontend_fee, sigma):
    """
    strategy 1 to allocate cash flow, only annual investment is included,
    and equally allocated to goals
    """
    number_of_goals = len(goals)
    max_year = int(max(years)+2)
    years = [i+1 for i in years]
    max_frontend_fee = max(frontend_fee)
    achieved_goals, processed_goals, goal_year, flag = 0, 0, 0, 0
    remaining_goals = number_of_goals
    annual_investment_per_goal = annual_investment/number_of_goals
    ai_per_goal_adjusted = annual_investment_per_goal
    shortfall_list = np.zeros(number_of_goals, dtype=float)
    surplus_list = np.zeros(number_of_goals, dtype=float)
    target_met = np.zeros(number_of_goals, dtype=int)

    present_value = []
    for i in range(number_of_goals):
        present_value.append(hp.calculate_pv(goals[i], years[i], ir_per_goal[i]))

    goals_list = []  # the list to store the goal arrays
    for j in range(number_of_goals):
        ai_required_per_year, ai_investment, ai_shortfall, ai_surplus, annual_goal_met, fee \
            = (np.zeros(int(years[j]), dtype=float) for i in range(6))
        goal1 = np.array((ai_required_per_year, ai_investment, ai_shortfall, \
            ai_surplus, annual_goal_met, fee))
        goals_list.append(goal1.T)

    ai_required, ai_required_pv = \
        (np.zeros(int(number_of_goals), dtype=float) for i in range(2))
    for i in range(number_of_goals):
        ai_required_pv[i] = hp.calculate_pv(goals[i], years[i]-1, ir_per_goal[i])
        ai_required[i] = \
        (ai_required_pv[i] * ir_per_goal[i])/(1-math.pow(1+ir_per_goal[i], -(years[i]-1)))
        #ai_required[i] = ((ai_required_pv[i] * (1 + ir_per_goal[i])) * \
        #(1 - (1 / (1 + ir_per_goal[i])))) / (1 - math.pow((1 / (1 + ir_per_goal[i])), years[i]))

    ai_required_pv_adjusted, ai_required_adjusted = \
        (np.zeros(number_of_goals, dtype=float) for i in range(2))
    total_ai_surplus, total_ai_shortfall = (np.zeros(max_year-1, dtype=float) for i in range(2))

    #------------ the main body to process the cash flow year by year
    for i in range(0, max_year):
        if i == 0:
            continue
        total_ai_remaining = 0
        if i in years:   # processing when the i falls in the full term year for one goal
            goal_year = years.index(i)
            next_goal = goal_year+1
            processed_goals += 1
            remaining_goals = number_of_goals - processed_goals
            if goals_list[goal_year][i-1, 4] == 1 or \
                (goals_list[goal_year][i-1][0]-goals_list[goal_year][i-1][1]) < 0.1:
            # judge whether the processed goal is achieved ?
                achieved_goals += 1
                target_met[goal_year] = 1
            if i == max_year-1:  # quit when i = max(years)
                processed_goals += 1
                break
        # adjust the annual required investment for the remaining goals
            ai_per_goal_adjusted = annual_investment/remaining_goals
            while next_goal < number_of_goals:
                accumulated_amount = 0
                for k in range(0, int(years[goal_year])):
                    each_amount = goals_list[next_goal][k][1]*\
                        (1+ir_per_goal[next_goal])**(years[next_goal]-k-1)
                    accumulated_amount += each_amount
                year_remain = years[next_goal] - years[goal_year]
                remaining_amount = goals[next_goal] - accumulated_amount
                ai_required_pv_adjusted[next_goal] = \
                    hp.calculate_pv(remaining_amount, year_remain, ir_per_goal[next_goal])
                ai_required_adjusted[next_goal] = \
                    (((ai_required_pv_adjusted[next_goal] * (1 + ir_per_goal[next_goal])) * \
                    (1 - (1 / (1 + ir_per_goal[next_goal])))) / (1 - math.pow(\
                    (1 / (1 + ir_per_goal[next_goal])), year_remain)))
                goals_list[next_goal][i][0] = ai_required_adjusted[next_goal]
                next_goal += 1
                flag = 1

        # fill in the year i data for the remaining unprocessed goals
        for j in range(min(achieved_goals, processed_goals), number_of_goals):
            if i >= years[j]:
                continue

            goals_list[j][i][0] = ai_required[j]
            goals_list[j][i][1] = annual_investment_per_goal

            if flag == 0:
                if goals_list[j][i][0] <= goals_list[j][i][1]*(1-frontend_fee[j]) \
                    or goals_list[j][i][0] - goals_list[j][i][1]*(1-frontend_fee[j]) < 0.1:
                    goals_list[j][i][1] = goals_list[j][i][0]
                    goals_list[j][i][5] = goals_list[j][i][1] * frontend_fee[j]
                    goals_list[j][i][3] = annual_investment_per_goal - \
                                            goals_list[j][i][0]-goals_list[j][i][5]
                    goals_list[j][i][4] = 1
                    total_ai_surplus[i] += goals_list[j][i][3]
                else:
                    goals_list[j][i][5] = goals_list[j][i][1] * frontend_fee[j]
                    goals_list[j][i][1] = goals_list[j][i][1]*(1-frontend_fee[j])
                    goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                    goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                    total_ai_shortfall[i] += goals_list[j][i][2]
            if flag == 1:
                goals_list[j][i][0] = ai_required_adjusted[j]
                goals_list[j][i][1] = ai_per_goal_adjusted
                if goals_list[j][i][0] <= goals_list[j][i][1]*(1-frontend_fee[j]):
                    goals_list[j][i][1] = goals_list[j][i][0]
                    goals_list[j][i][5] = goals_list[j][i][1]*frontend_fee[j]
                    goals_list[j][i][3] = ai_per_goal_adjusted \
                                            - goals_list[j][i][1]-goals_list[j][i][5]
                    goals_list[j][i][4] = 1
                    total_ai_surplus[i] += goals_list[j][i][3]
                else:
                    goals_list[j][i][5] = goals_list[j][i][1]*frontend_fee[j]
                    goals_list[j][i][1] = ai_per_goal_adjusted*(1-frontend_fee[j])
                    goals_list[j][i][2] = (goals_list[j][i][0] - goals_list[j][i][1])
                    goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                    total_ai_shortfall[i] += goals_list[j][i][2]

 #if the processed goal has surplus,
 #the surplus is equally allocated to the remaining unachieved goals
        surplus_to_per_goal = 0
        count = int(0)
        for j in range(processed_goals, number_of_goals):
            # count the number of goals with unmet amount in the year
            if goals_list[j][i][4] == 0:
                count += 1
        total_ai_remaining = total_ai_surplus[i]

        while total_ai_remaining > 0.1 and count > 0:
            # the total surplus in the year is equally distributed to goals with unmet amount
            surplus_to_per_goal = total_ai_remaining/count
            for j in range(processed_goals, number_of_goals):
                if goals_list[j][i][4] < 0.1:
                    if (goals_list[j][i][1] + surplus_to_per_goal*(1-frontend_fee[j])) \
                                                    >= goals_list[j][i][0]:
                        goals_list[j][i][3] = surplus_to_per_goal - \
                                                goals_list[j][i][2]*(1+frontend_fee[j])
                        goals_list[j][i][1] = goals_list[j][i][0]
                        goals_list[j][i][5] += goals_list[j][i][2]*frontend_fee[j]
                        goals_list[j][i][4] = 1
                        total_ai_shortfall[i] -= goals_list[j][i][2]
                        total_ai_remaining = total_ai_remaining - \
                                                surplus_to_per_goal + goals_list[j][i][3]
                        count -= 1
                    else:
                        goals_list[j][i][1] += surplus_to_per_goal*(1-frontend_fee[j])
                        goals_list[j][i][2] = (goals_list[j][i][0]- goals_list[j][i][1])
                        goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                        goals_list[j][i][5] += surplus_to_per_goal*frontend_fee[j]
                        total_ai_remaining -= surplus_to_per_goal
                        total_ai_shortfall[i] -= surplus_to_per_goal
        total_ai_surplus[i] = total_ai_remaining

    shortfall_list, surplus_list = pp.getting_shortfall_surplus(\
        1, goals, years, ir_per_goal, goals_list, target_met, max_frontend_fee)
    probs_list = hp.probability_of_goals(goals, years, ir_per_goal, sigma, goals_list, surplus_list)

    return target_met, shortfall_list, surplus_list, probs_list, goals_list

## ----------------------- strategy 2 -----------------------
def calculator_ai_priority(goals, goal_priority, years, annual_investment, \
                            ir_per_goal, frontend_fee, sigma):
    """
    strategy 2 to allocate cash flow, only annual investment is included,
    and allocated to goals by goal-priority
    """
    number_of_goals = len(goals)
    max_year = int(max(years))+2
    years = [i+1 for i in years]
    max_frontend_fee = max(frontend_fee)
    achieved_goals, processed_goals, goal_year, flag = 0, 0, 0, 0
    shortfall_list = np.zeros(number_of_goals, dtype=float)
    surplus_list = np.zeros(number_of_goals, dtype=float)
    target_met = np.zeros(number_of_goals, dtype=int)

    present_value = []
    present_value.append((hp.calculate_pv(goals[i], years[i]-1, \
                        ir_per_goal[i])) for i in range(number_of_goals))

    goals_list = []   # the list to store the goal arrays
    for j in range(number_of_goals):
        ai_required_per_year = np.zeros(int(years[j]), dtype=float)
        ai_investment = np.zeros(int(years[j]), dtype=float)
        ai_shortfall = np.zeros(int(years[j]), dtype=float)
        ai_surplus = np.zeros(int(years[j]), dtype=float)
        annual_goal_met = np.zeros(int(years[j]), dtype=float)
        fee = np.zeros(int(years[j]), dtype=float)
        goal1 = np.array((ai_required_per_year, ai_investment, \
                            ai_shortfall, ai_surplus, annual_goal_met, fee))
        goals_list.append(goal1.T)

    ai_required, ai_required_pv = (np.zeros(int(number_of_goals), dtype=float) for i in range(2))
    for i in range(number_of_goals):
        ai_required_pv[i] = hp.calculate_pv(goals[i], years[i]-1, ir_per_goal[i])
        ai_required[i] = ((ai_required_pv[i] * (1 + ir_per_goal[i])) * \
            (1 - (1 / (1 + ir_per_goal[i])))) / (1 - math.pow((1 / (1 + ir_per_goal[i])), years[i]-1))

    ai_required_adjusted = np.zeros(number_of_goals, dtype=float)
    ai_required_pv_adjusted = np.zeros(number_of_goals, dtype=float)
    #-- the main body to process the cash flow year by year
    for i in range(0, max_year):
        if i == 0 :
            continue
        goal_priority_temp = goal_priority[:]
        if i in years:  # processing when the i falls in the full term year for one goal
            goal_year = years.index(i)
            next_goal = goal_year+1
            processed_goals += 1

            if goals_list[goal_year][i-1][4] > 0.1:
                achieved_goals += 1
                target_met[goal_year] = 1
            if i == max_year-1:  # quit when i = max(years)
                if goals_list[goal_year][:, 4].any() or \
                        goals_list[goal_year][i-1][0]- goals_list[goal_year][i-1][1] < 0.1:
                    goals_list[goal_year][i-1][4] = 1
                    target_met[goal_year] = 1

            while next_goal < number_of_goals:
                accumulated_amount = 0
                for k in range(0, int(years[goal_year])):
                    each_amount = goals_list[next_goal][k][1]*\
                                    (1+ir_per_goal[next_goal])**(years[next_goal]-k-1)
                    accumulated_amount += each_amount
                remaining_amount = goals[next_goal] - accumulated_amount
                year_remain = years[next_goal] - years[goal_year]
                ai_required_pv_adjusted[next_goal] = \
                        hp.calculate_pv(remaining_amount, year_remain, ir_per_goal[next_goal])
                ai_required_adjusted[next_goal] = (((ai_required_pv_adjusted[next_goal] * \
                        (1 + ir_per_goal[next_goal])) * \
                        (1 - (1 / (1 + ir_per_goal[next_goal])))) / (1 - \
                            math.pow((1 / (1 + ir_per_goal[next_goal])), year_remain)))
                next_goal += 1
                flag = 1

        # fill in the year i data for the remaining unprocessed goals
        ai_remaining = annual_investment
        ai_shortfall = 0
        count = number_of_goals
        while count > 0:
            j = goal_priority_temp.index(min(goal_priority_temp))

            if i >= years[j]:
                count -= 1
                goal_priority_temp[j] = 100
                continue
            goals_list[j][i][0] = ai_required[j]
            if flag == 0:
                if goals_list[j][i][0] <= ai_remaining*(1-frontend_fee[j]):
                    goals_list[j][i][1] = goals_list[j][i][0]
                    goals_list[j][i][5] = goals_list[j][i][0]*frontend_fee[j]
                    goals_list[j][i][3] = ai_remaining - goals_list[j][i][0]-goals_list[j][i][5]
                    ai_remaining = goals_list[j][i][3]
                    goals_list[j][i][4] = 1
                    target_met[j] = 1
                else:
                    goals_list[j][i][1] = ai_remaining *(1-frontend_fee[j])
                    goals_list[j][i][5] = ai_remaining * frontend_fee[j]
                    ai_remaining = 0
                    ai_shortfall += goals_list[j][i][0] - goals_list[j][i][1]
                    goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                    goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
            if flag == 1:
                goals_list[j][i][0] = ai_required_adjusted[j]
                if goals_list[j][i][0] <= ai_remaining*(1-frontend_fee[j]) or \
                        abs(goals_list[j][i][0]-ai_remaining*(1-frontend_fee[j])) < 0.1:
                    goals_list[j][i][1] = goals_list[j][i][0]
                    goals_list[j][i][5] = goals_list[j][i][1]*frontend_fee[j]
                    goals_list[j][i][3] = ai_remaining - goals_list[j][i][1]-goals_list[j][i][5]
                    ai_remaining = goals_list[j][i][3]
                    goals_list[j][i][4] = 1
                    target_met[j] = 1
                else:
                    goals_list[j][i][1] = ai_remaining*(1-frontend_fee[j])
                    goals_list[j][i][5] = ai_remaining*frontend_fee[j]
                    ai_remaining = 0
                    ai_shortfall += (goals_list[j][i][0] - goals_list[j][i][1])
                    goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                    goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0

            count -= 1
            goal_priority_temp[j] = 100

    shortfall_list, surplus_list = pp.getting_shortfall_surplus(\
            2, goals, years, ir_per_goal, goals_list, target_met, max_frontend_fee)
    probs_list = hp.probability_of_goals(goals, years, ir_per_goal, sigma, goals_list, surplus_list)
    return target_met, shortfall_list, surplus_list, probs_list, goals_list

## ----------------------- strategy 3 -----------------------
def calculator_ii_ai_equal(goals, years, initial_investment, \
                            annual_investment, ir_per_goal, frontend_fee, sigma):
    """
    strategy 3 to allocate cash flow, both annual_investment and initial_investmentare
    equally allocated to goals
    """
    number_of_goals = len(goals)
    max_year = int(max(years)+2)
    years = [i+1 for i in years]
    max_frontend_fee = max(frontend_fee)
    achieved_goals, processed_goals = 0, 0

    remaining_goals, remaining_goals_to_process, remaining_goals_to_achieve = \
                                                (number_of_goals for i in range(3))
    initial_investment_per_goal = initial_investment/number_of_goals

    shortfall_list, surplus_list = (np.zeros(number_of_goals, dtype=float) for i in range(2))
    target_met = np.zeros(number_of_goals, dtype=int)
    ai_required_per_goal_adjusted = 0
    present_value = []
    for i in range(number_of_goals):
        present_value.append(hp.calculate_pv(goals[i], years[i]-1, ir_per_goal[i]))

    goals_list = [] # the list to store the goal arrays
    for j in range(number_of_goals):
        ai_required_per_year = np.zeros(int(years[j]), dtype=float)
        ai_investment = np.zeros(int(years[j]), dtype=float)
        ai_shortfall = np.zeros(int(years[j]), dtype=float)
        ai_surplus = np.zeros(int(years[j]), dtype=float)
        annual_goal_met = np.zeros(int(years[j]), dtype=float)
        fee = np.zeros(int(years[j]), dtype=float)

        goal1 = np.array((ai_required_per_year, ai_investment, ai_shortfall, \
                            ai_surplus, annual_goal_met, fee))
        goals_list.append(goal1.T)

    total_ai_remaining = 0
    total_ai_surplus, total_ai_shortfall = (np.zeros(max_year, dtype=float) for i in range(2))

    #- the main body to process the cash flow year by year
    for i in range(0, max_year):
        remaining_goals_to_process = number_of_goals - processed_goals
        remaining_goals_to_achieve = number_of_goals - achieved_goals

        if remaining_goals_to_process == 0 and remaining_goals_to_achieve == 0:
            break
        if remaining_goals_to_process != 0 and remaining_goals_to_achieve == 0:
            break
        if remaining_goals_to_process > 0 or remaining_goals_to_achieve > 0:
            if i == 0:
                for j in range(number_of_goals):
                    goals_list[j][i][0] = present_value[j]
                    goals_list[j][i][1] = initial_investment_per_goal*(1-frontend_fee[j])
                    goals_list[j][i][5] = initial_investment_per_goal* frontend_fee[j]
                    if goals_list[j][i][0] <= goals_list[j][i][1] \
                                or goals_list[j][i][0] - goals_list[j][i][1] < 0.1:
                        goals_list[j][i][1] = goals_list[j][i][0]
                        goals_list[j][i][3] = initial_investment_per_goal - \
                                                goals_list[j][i][1] - goals_list[j][i][5]
                        goals_list[j][i][4] = 1
                        achieved_goals += 1
                        target_met[j] = 1
                        total_ai_surplus[i] += goals_list[j][i][3]
                    else:
                        goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                        ai_required_per_goal_adjusted = goals_list[j][i][2]
                        goals_list[j][i+1][0] = ai_required_per_goal_adjusted
                        total_ai_shortfall[i] += goals_list[j][i][2]
            else:
                if i in years:
                    goal_year = years.index(i)
                    if (goals_list[goal_year][i-1][0] <= goals_list[goal_year][i-1][1]) \
                            or ((goals_list[goal_year][i-1][0] - \
                                    goals_list[goal_year][i-1][1]) < 0.1):
                        goals_list[goal_year][i-1][4] = 1
                        target_met[goal_year] = 1
                    processed_goals += 1

                    if i == max_year-1:
                        if goals_list[goal_year][i-1][0]-goals_list[goal_year][i-1][1] < 0.1:
                            goals_list[goal_year][i-1][4] = 1
                            target_met[goal_year] = 1
                            processed_goals += 1
                            break

                    for k in range(max(processed_goals, achieved_goals), number_of_goals):
                        if goals_list[k][i-1][4] == 1.:
                            achieved_goals += 1
                            target_met[k] = 1

                    remaining_goals = number_of_goals - max(processed_goals, achieved_goals)

                if remaining_goals > 0:
                    ai_per_goal_adjusted = annual_investment/remaining_goals

                for j in range(min(processed_goals, achieved_goals), number_of_goals):
                    if i >= years[j]:
                        continue
                    if goals_list[j][i-1][4] > 0.1:
                        goals_list[j][i][4] = 1.
                        continue
                    elif goals_list[j][i-1][4] < 0.1:
                        ai_required_per_goal_adjusted = \
                                        goals_list[j][i-1][2] *(1+ir_per_goal[j])
                        goals_list[j][i][0] = ai_required_per_goal_adjusted
                        goals_list[j][i][1] = ai_per_goal_adjusted\
                                                * (1-frontend_fee[j])

                        if goals_list[j][i][0] <= goals_list[j][i][1] \
                                or goals_list[j][i][0] - goals_list[j][i][1] < 0.1:
                            goals_list[j][i][1] = goals_list[j][i][0]
                            goals_list[j][i][5] = goals_list[j][i][1] * frontend_fee[j]
                            goals_list[j][i][3] = ai_per_goal_adjusted - \
                                                    goals_list[j][i][0] - goals_list[j][i][5]
                            goals_list[j][i][4] = 1
                            achieved_goals += 1
                            remaining_goals -= 1
                            target_met[j] = 1
                            total_ai_surplus[i] += goals_list[j][i][3]
                        if goals_list[j][i][0] > goals_list[j][i][1]:
                            goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                            goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                            goals_list[j][i][5] = ai_per_goal_adjusted \
                                                    * frontend_fee[j]
                            total_ai_shortfall[i] += goals_list[j][i][2]

    #if the processed goal has surplus, the surplus is equally allocated to the remaining unmet goal
            surplus_to_per_goal = 0
            count = int(0)
            for j in range(max(processed_goals, achieved_goals), number_of_goals):
                if goals_list[j][i][4] == 0:
                    count += 1

            total_ai_remaining = total_ai_surplus[i]
            while total_ai_remaining > 0.1 and count != 0:
                surplus_to_per_goal = total_ai_remaining/count
                for j in range(max(processed_goals, achieved_goals), number_of_goals):
                    if goals_list[j][i][4] < 0.1:
                        if (goals_list[j][i][1] + surplus_to_per_goal*(1-frontend_fee[j])) \
                                                            >= goals_list[j][i][0] \
                                or (goals_list[j][i][0] - (goals_list[j][i][1] + \
                                    surplus_to_per_goal*(1-frontend_fee[j]))) < 0.1:
                            goals_list[j][i][3] = goals_list[j][i][1] + \
                                surplus_to_per_goal*(1-frontend_fee[j]) - goals_list[j][i][0]
                            goals_list[j][i][1] = goals_list[j][i][0]
                            goals_list[j][i][5] += surplus_to_per_goal*frontend_fee[j]
                            goals_list[j][i][4] = 1
                            total_ai_shortfall[i] -= goals_list[j][i][2]
                            total_ai_remaining = total_ai_remaining - \
                                                    surplus_to_per_goal + goals_list[j][i][3]
                            count -= 1
                        else:
                            goals_list[j][i][1] += surplus_to_per_goal*(1-frontend_fee[j])
                            goals_list[j][i][5] += surplus_to_per_goal*frontend_fee[j]
                            goals_list[j][i][2] = goals_list[j][i][0]- goals_list[j][i][1]
                            goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                            total_ai_remaining -= surplus_to_per_goal
                            total_ai_shortfall[i] -= surplus_to_per_goal
            total_ai_surplus[i] = total_ai_remaining

    shortfall_list, surplus_list = pp.getting_shortfall_surplus(\
            3, goals, years, ir_per_goal, goals_list, target_met, max_frontend_fee)
    probs_list = hp.probability_of_goals(goals, years, ir_per_goal, sigma, goals_list, surplus_list)
    return target_met, shortfall_list, surplus_list, probs_list, goals_list

## ----------------------- strategy 4 -----------------------
def calculator_ii_ai_priority(goals, goal_priority, years, initial_investment,\
                    annual_investment, ir_per_goal, frontend_fee, sigma):
    """
    strategy 4 to allocate cash flow, both annual_investment and initial_investment are
    allocated to goals by goal_priority
    """
    number_of_goals = len(goals)
    max_year = int(max(years)+2)
    years = [i+1 for i in years]
    max_frontend_fee = max(frontend_fee)
    achieved_goals, processed_goals = 0, 0

    remaining_goals_to_process = number_of_goals
    remaining_goals_to_achieve = number_of_goals
    remaining_initial_investment = initial_investment

    shortfall_list, surplus_list = (np.zeros(number_of_goals, dtype=float) for i in range(2))
    target_met = np.zeros(number_of_goals, dtype=int)
    ai_required_per_goal_adjusted = 0
    present_value = []
    for i in range(0, number_of_goals):
        present_value.append(hp.calculate_pv(goals[i], years[i]-1, ir_per_goal[i]))

    ### the list to store the goal arrays
    goals_list = []
    for j in range(number_of_goals):
        ai_required_per_year = np.zeros(int(years[j]), dtype=float)
        ai_investment = np.zeros(int(years[j]), dtype=float)
        ai_shortfall = np.zeros(int(years[j]), dtype=float)
        ai_surplus = np.zeros(int(years[j]), dtype=float)
        annual_goal_met = np.zeros(int(years[j]), dtype=float)
        fee = np.zeros(int(years[j]), dtype=float)
        goal1 = np.array((ai_required_per_year, \
                    ai_investment, ai_shortfall, ai_surplus, annual_goal_met, fee))
        goals_list.append(goal1.T)

    total_ai_surplus, total_ai_shortfall = (np.zeros(max_year, dtype=float) for i in range(2))

    #-the main body to process the cash flow year by year
    goal_priority_temp = goal_priority[:]

    for i in range(0, max_year):
        remaining_goals_to_process = number_of_goals - processed_goals
        remaining_goals_to_achieve = number_of_goals - achieved_goals
        remaining_annual_investment = annual_investment

        if remaining_goals_to_process == 0 and remaining_goals_to_achieve == 0:
            break
        #if remaining_goals_to_process > 0.1 and remaining_goals_to_achieve == 0:
         #   break
        else:
        #if remaining_goals_to_process > 0.1 or remaining_goals_to_achieve > 0.1:
            if i == 0:
                for k in range(number_of_goals):
                    goals_list[k][i][0] = present_value[k]

                count = len(goals)
                while count > 0:
                    j = goal_priority_temp.index(min(goal_priority_temp))

                    if goals_list[j][i][0] <= remaining_initial_investment*(1-frontend_fee[j]) \
                            or (goals_list[j][i][0] - \
                                remaining_initial_investment*(1-frontend_fee[j])) < 0.1:
                        goals_list[j][i][1] = goals_list[j][i][0]
                        goals_list[j][i][5] = goals_list[j][i][1]*frontend_fee[j]
                        goals_list[j][i][3] = remaining_initial_investment - \
                                                goals_list[j][i][0]-goals_list[j][i][5]
                        remaining_initial_investment = remaining_initial_investment - \
                                                goals_list[j][i][0]-goals_list[j][i][5]
                        goals_list[j][i][4] = 1
                        achieved_goals += 1
                        target_met[j] = 1
                        #count -= 1
                    elif goals_list[j][i][0] > remaining_initial_investment*(1-frontend_fee[j]):
                        goals_list[j][i][1] = remaining_initial_investment*(1-frontend_fee[j])
                        goals_list[j][i][5] = remaining_initial_investment*frontend_fee[j]
                        goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                        remaining_initial_investment = 0
                        ai_required_per_goal_adjusted = \
                                                    goals_list[j][i][2] *(1+ir_per_goal[j])
                        goals_list[j][i+1][0] = ai_required_per_goal_adjusted
                        total_ai_shortfall[i] += goals_list[j][i][2]
                    count -= 1

                    goal_priority_temp[j] = 100
                if remaining_initial_investment > 0.1:
                    print('All the goals can be met at the initial investment')
                    break
            else:
                goal_priority_temp1 = goal_priority[:]
                if i in years:
                    goal_year = years.index(i)
                    if (goals_list[goal_year][i-1][0] <= goals_list[goal_year][i-1][1]) \
                        or ((goals_list[goal_year][i-1][0] - goals_list[goal_year][i-1][1]) < 0.1):
                        target_met[goal_year] = 1
                    processed_goals += 1

                    if i == max_year-1:
                        if goals_list[goal_year][:, 4].any() \
                            or goals_list[goal_year][i-1][0]-goals_list[goal_year][i-1][1] < 0.1:
                            goals_list[goal_year][i-1][4] = 1
                            target_met[goal_year] = 1
                            processed_goals += 1
                            break

                    for k in range(max(processed_goals, achieved_goals), number_of_goals):
                        if goals_list[k][i-1][4] == 1.:
                            achieved_goals += 1
                            target_met[k] = 1

                count = len(goals)
                while count > 0:
                    j = goal_priority_temp1.index(min(goal_priority_temp1))

                    if i >= years[j]:
                        count -= 1
                        goal_priority_temp1[j] = 100
                        continue
                    if goals_list[j][i-1][4] > 0.1:
                        goals_list[j][i][4] = 1
                    else:
                        ai_required_per_goal_adjusted = \
                                        goals_list[j][i-1][2]*(1+ir_per_goal[j])
                        goals_list[j][i][0] = ai_required_per_goal_adjusted
                        if goals_list[j][i][0] <= remaining_annual_investment*(1-frontend_fee[j]):
                            goals_list[j][i][1] = goals_list[j][i][0]
                            goals_list[j][i][5] = goals_list[j][i][1]*frontend_fee[j]
                            goals_list[j][i][3] = remaining_annual_investment - \
                                                    goals_list[j][i][0]-goals_list[j][i][5]
                            remaining_annual_investment = remaining_annual_investment - \
                                                            goals_list[j][i][0]-goals_list[j][i][5]

                            goals_list[j][i][4] = 1
                            achieved_goals += 1
                            target_met[j] = 1
                            if j+1 < number_of_goals and goals_list[j+1][i][4] > 0.1:
                                total_ai_surplus[i] += goals_list[j][i][3]
                            if j == number_of_goals-1:
                                total_ai_surplus[i] = goals_list[j][i][3]

                        else:
                            goals_list[j][i][1] = remaining_annual_investment*(1-frontend_fee[j])
                            goals_list[j][i][5] = remaining_annual_investment*frontend_fee[j]
                            goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                            goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                            total_ai_shortfall[i] += goals_list[j][i][2]
                            remaining_annual_investment = 0

                    count -= 1
                    goal_priority_temp1[j] = 100

    shortfall_list, surplus_list = pp.getting_shortfall_surplus(\
                4, goals, years, ir_per_goal, goals_list, target_met, max_frontend_fee)
    probs_list = hp.probability_of_goals(goals, years, ir_per_goal, sigma, goals_list, surplus_list)
    return target_met, shortfall_list, surplus_list, probs_list, goals_list

## --------------- strategy 5 ------------------
def calculator_ii_equal_ai_priority(goals, goal_priority, years, initial_investment,\
                    annual_investment, ir_per_goal, frontend_fee, sigma):
    """
    strategy 5 to allocate cash flow, initial_investment is equally allocated to goals,
    and annual_investment is allocated to goals by goal_priority
    """
    number_of_goals = len(goals)
    max_year = int(max(years)+2)
    years = [i+1 for i in years]
    max_frontend_fee = max(frontend_fee)
    achieved_goals, processed_goals = 0, 0
    remaining_goals_to_process = number_of_goals
    remaining_goals_to_achieve = number_of_goals
    initial_investment_per_goal = initial_investment/number_of_goals
    shortfall_list, surplus_list = (np.zeros(number_of_goals, dtype=float) for i in range(2))
    target_met = np.zeros(number_of_goals, dtype=int)
    ai_required_per_goal_adjusted = 0
    present_value = []
    for i in range(0, number_of_goals):
        present_value.append(hp.calculate_pv(goals[i], years[i]-1, ir_per_goal[i]))

    goals_list = []   # the list to store the cash flow arrays
    for j in range(number_of_goals):
        ai_required_per_year = np.zeros(int(years[j]), dtype=float)
        ai_investment = np.zeros(int(years[j]), dtype=float)
        ai_shortfall = np.zeros(int(years[j]), dtype=float)
        ai_surplus = np.zeros(int(years[j]), dtype=float)
        annual_goal_met = np.zeros(int(years[j]), dtype=float)
        fee = np.zeros(int(years[j]), dtype=float)
        goal1 = np.array((ai_required_per_year, ai_investment, \
                            ai_shortfall, ai_surplus, annual_goal_met, fee))
        goals_list.append(goal1.T)


    total_ai_surplus, total_ai_shortfall = (np.zeros(max_year, dtype=float) for i in range(2))

    # the main body to process the cash flow year by year
    for i in range(0, max_year):
        total_ii_surplus = 0
        remaining_goals_to_process = number_of_goals - processed_goals
        remaining_goals_to_achieve = number_of_goals - achieved_goals
        remaining_annual_investment = annual_investment

        if remaining_goals_to_process == 0 and remaining_goals_to_achieve == 0:
            break
        if remaining_goals_to_process != 0 and remaining_goals_to_achieve == 0:
            break
        if remaining_goals_to_process > 0 or remaining_goals_to_achieve > 0:
            if i == 0:
                for j in range(number_of_goals):
                    goals_list[j][i][0] = present_value[j]
                    if goals_list[j][i][0] <= initial_investment_per_goal*(1-frontend_fee[j]):
                        goals_list[j][i][1] = goals_list[j][i][0]
                        goals_list[j][i][5] = goals_list[j][i][1]*(frontend_fee[j])
                        goals_list[j][i][3] = initial_investment_per_goal - \
                                                goals_list[j][i][0] - goals_list[j][i][5]
                        goals_list[j][i][4] = 1
                        total_ii_surplus += goals_list[j][i][3]
                        achieved_goals += 1
                        target_met[j] = 1
                    else:
                        goals_list[j][i][1] = initial_investment_per_goal*(1-frontend_fee[j])
                        goals_list[j][i][5] = initial_investment_per_goal*(frontend_fee[j])
                        goals_list[j][i][2] = goals_list[j][i][0] - \
                                                initial_investment_per_goal*(1-frontend_fee[j])
                        goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                        #total_ii_shortfall += goals_list[j][i][2]

                        ai_required_per_goal_adjusted = goals_list[j][i][2]*(1+ir_per_goal[j])
                        goals_list[j][i+1][0] = ai_required_per_goal_adjusted

                surplus_to_per_goal = 0
                count = int(0)
                for j in range(achieved_goals, number_of_goals):
                    # count the number of goals with unmet amount in the year
                    if goals_list[j][i][4] == 0:
                        count += 1

                while total_ii_surplus > 0.1 and count > 0:
                # the total surplus is equally distributed to goals with unmet amount
                    surplus_to_per_goal = total_ii_surplus/count
                    for j in range(processed_goals, number_of_goals):
                        if goals_list[j][i][4] < 0.1:
                            if (goals_list[j][i][1] + surplus_to_per_goal*(1-frontend_fee[j])) \
                                                            >= goals_list[j][i][0]:
                                goals_list[j][i][3] = surplus_to_per_goal - \
                                                        goals_list[j][i][2]*(1+frontend_fee[j])
                                goals_list[j][i][1] = goals_list[j][i][0]
                                goals_list[j][i][5] += goals_list[j][i][2]*frontend_fee[j]
                                goals_list[j][i][4] = 1
                                total_ai_shortfall[i] -= goals_list[j][i][2]
                                total_ii_surplus = total_ii_surplus - \
                                                    surplus_to_per_goal + goals_list[j][i][3]
                                count -= 1
                            else:
                                goals_list[j][i][1] += surplus_to_per_goal*(1-frontend_fee[j])
                                goals_list[j][i][2] = (goals_list[j][i][0]- goals_list[j][i][1])
                                goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                                goals_list[j][i][5] += surplus_to_per_goal*frontend_fee[j]
                                total_ii_surplus -= surplus_to_per_goal
                                #total_ai_shortfall[i] -= surplus_to_per_goal
                #total_ai_surplus[i] = total_ai_remaining
                ##################
                if total_ii_surplus > 0.1:
                    print('All the goals can be met at the initial investment')
                    break
            else:
                goal_priority_temp = goal_priority[:]
                if i in years:
                    goal_year = years.index(i)
                    processed_goals += 1

                    if i == max_year-1:
                        if goals_list[goal_year][:, 4].any() \
                            or goals_list[goal_year][i-1][0]- goals_list[goal_year][i-1][1] < 0.1:
                            goals_list[goal_year][i-1][4] = 1
                            target_met[goal_year] = 1
                            processed_goals += 1
                            break

                    for k in range(max(processed_goals, achieved_goals), number_of_goals):
                        if goals_list[k][0:i-1, 4].any() > 0.1:
                            achieved_goals += 1
                            target_met[k] = 1

                count = len(goals)
                while count > 0:
                    j = goal_priority_temp.index(min(goal_priority_temp))

                    if i >= years[j]:
                        count -= 1
                        goal_priority_temp[j] = 100
                        continue

                    if goals_list[j][i-1][4] > 0.1:
                        goals_list[j][i][4] = 1

                    else:
                        ai_required_per_goal_adjusted = \
                                            goals_list[j][i-1][2]*(1+ir_per_goal[j])
                        goals_list[j][i][0] = ai_required_per_goal_adjusted
                        if goals_list[j][i][0] <= remaining_annual_investment*(1-frontend_fee[j]):
                            goals_list[j][i][1] = goals_list[j][i][0]
                            goals_list[j][i][5] = goals_list[j][i][1] * frontend_fee[j]
                            goals_list[j][i][3] = remaining_annual_investment - \
                                                    goals_list[j][i][1]-goals_list[j][i][5]
                            remaining_annual_investment = goals_list[j][i][3]
                            goals_list[j][i][4] = 1
                            achieved_goals += 1
                            target_met[j] = 1
                            total_ai_surplus[i] += goals_list[j][i][3]
                        else:
                            goals_list[j][i][1] = remaining_annual_investment*(1-frontend_fee[j])
                            goals_list[j][i][5] = remaining_annual_investment*frontend_fee[j]
                            goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                            goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                            remaining_annual_investment = 0
                            total_ai_shortfall[i] += goals_list[j][i][2]
                             #goals_list[j][i][4] = 0
                    count -= 1
                    goal_priority_temp[j] = 100

    shortfall_list, surplus_list = pp.getting_shortfall_surplus(\
            5, goals, years, ir_per_goal, goals_list, target_met, max_frontend_fee)
    probs_list = hp.probability_of_goals(goals, years, ir_per_goal, sigma, goals_list, surplus_list)

    return target_met, shortfall_list, surplus_list, probs_list, goals_list

## --------------- strategy 6 ------------------
def calculator_ii_priority_ai_equal(goals, goal_priority, years, initial_investment, \
            annual_investment, ir_per_goal, frontend_fee, sigma):
    """
    strategy 6 to allocate cash flow, annual_investment is equally allocated to goals,
    and initial_investment is allocated to goals by goal_priority
    """
    number_of_goals = len(goals)
    max_year = int(max(years)+2)
    years = [i+1 for i in years]
    max_frontend_fee = max(frontend_fee)
    achieved_goals, processed_goals = 0, 0

    remaining_goals, remaining_goals_to_process, remaining_goals_to_achieve = \
                                                (number_of_goals for i in range(3))
    remaining_initial_investment = initial_investment

    shortfall_list, surplus_list = (np.zeros(number_of_goals, dtype=float) for i in range(2))
    target_met = np.zeros(number_of_goals, dtype=int)
    ai_required_per_goal_adjusted = 0

    present_value = []
    for i in range(0, number_of_goals):
        present_value.append(hp.calculate_pv(goals[i], years[i]-1, ir_per_goal[i]))

    goals_list = []  # the list to store the goal arrays
    for j in range(number_of_goals):
        ai_required_per_year = np.zeros(int(years[j]), dtype=float)
        ai_investment = np.zeros(int(years[j]), dtype=float)
        ai_shortfall = np.zeros(int(years[j]), dtype=float)
        ai_surplus = np.zeros(int(years[j]), dtype=float)
        annual_goal_met = np.zeros(int(years[j]), dtype=float)
        fee = np.zeros(int(years[j]), dtype=float)
        goal1 = np.array((ai_required_per_year, ai_investment, \
                            ai_shortfall, ai_surplus, annual_goal_met, fee))
        goals_list.append(goal1.T)

    total_ai_remaining = 0
    total_ai_surplus, total_ai_shortfall = (np.zeros(max_year, dtype=float) for i in range(2))
    annual_investment_per_goal = annual_investment/number_of_goals
    ai_per_goal_adjusted = annual_investment_per_goal

    goal_priority_temp = goal_priority[:]
    for i in range(0, max_year):
        remaining_goals_to_process = number_of_goals - processed_goals
        remaining_goals_to_achieve = number_of_goals - achieved_goals

        if remaining_goals_to_process == 0 and remaining_goals_to_achieve == 0:
            break
        if remaining_goals_to_process != 0 and remaining_goals_to_achieve == 0:
            break
        if remaining_goals_to_process > 0 or remaining_goals_to_achieve > 0:
            annual_investment_per_goal = annual_investment/remaining_goals_to_achieve
            if i == 0:
                for k in range(number_of_goals):
                    goals_list[k][i][0] = present_value[k]

                count = len(goals)
                while count > 0:
                    j = goal_priority_temp.index(min(goal_priority_temp))
                    goals_list[j][i][0] = present_value[j]
                    if goals_list[j][i][0] <= remaining_initial_investment*(1-frontend_fee[j]):
                        goals_list[j][i][1] = goals_list[j][i][0]
                        goals_list[j][i][5] = goals_list[j][i][1]*frontend_fee[j]
                        goals_list[j][i][3] = remaining_initial_investment - \
                                                goals_list[j][i][1]-goals_list[j][i][5]
                        remaining_initial_investment = remaining_initial_investment - \
                                                goals_list[j][i][1]-goals_list[j][i][5]
                        total_ai_surplus[i] += goals_list[j][i][3]
                        goals_list[j][i][4] = 1
                        achieved_goals += 1
                        target_met[j] = 1
                        remaining_goals = number_of_goals - max(processed_goals, achieved_goals)

                    elif goals_list[j][i][0] > remaining_initial_investment*(1-frontend_fee[j]):
                        goals_list[j][i][1] = remaining_initial_investment*(1-frontend_fee[j])
                        goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                        goals_list[j][i][5] = remaining_initial_investment*frontend_fee[j]
                        total_ai_shortfall[i] += goals_list[j][i][2]
                        remaining_initial_investment = 0
                        ai_required_per_goal_adjusted = goals_list[j][i][2]*(1+ir_per_goal[j])
                        goals_list[j][i+1][0] = ai_required_per_goal_adjusted
                    count -= 1
                    goal_priority_temp[j] = 100

                if remaining_initial_investment > 0.1:
                    print('All the goals can be met at the initial investment')
                    break
            else:
                if i in years:
                    goal_year = years.index(i)
                    processed_goals += 1

                    if i == max_year-1:
                        if goals_list[goal_year][:, 4].any() \
                            or goals_list[goal_year][i-1][0]- goals_list[goal_year][i-1][1] < 0.1:
                            goals_list[goal_year][i-1][4] = 1
                            target_met[goal_year] = 1
                            processed_goals += 1
                            break

                    for k in range(min(processed_goals, achieved_goals), number_of_goals):
                        if goals_list[k][0:i-1, 4].any() > 0.1:
                            achieved_goals += 1
                            target_met[k] = 1

                    remaining_goals = number_of_goals - max(processed_goals, achieved_goals)

                if remaining_goals > 0:
                    ai_per_goal_adjusted = annual_investment/remaining_goals
                else: break

                for j in range(min(processed_goals, achieved_goals), number_of_goals):
                    if i >= years[j]:
                        continue

                    if goals_list[j][i-1][4] > 0.1:
                        goals_list[j][i][4] = 1

                    elif goals_list[j][i-1][4] < 0.1 and i < max_year-1:
                        ai_required_per_goal_adjusted = \
                                        goals_list[j][i-1][2]*(1+ir_per_goal[j])
                        goals_list[j][i][0] = ai_required_per_goal_adjusted
                        goals_list[j][i][1] = ai_per_goal_adjusted
                        if goals_list[j][i][0] <= goals_list[j][i][1]*(1-frontend_fee[j]):
                            goals_list[j][i][5] = goals_list[j][i][0]*frontend_fee[j]
                            goals_list[j][i][3] = goals_list[j][i][1] - \
                                                    goals_list[j][i][0]-goals_list[j][i][5]
                            goals_list[j][i][1] = goals_list[j][i][0]
                            goals_list[j][i][4] = 1
                            achieved_goals += 1
                            target_met[j] = 1
                            remaining_goals -= 1
                            total_ai_surplus[i] += goals_list[j][i][3]
                        else:
                            goals_list[j][i][5] = goals_list[j][i][1] * frontend_fee[j]
                            goals_list[j][i][1] = goals_list[j][i][1] *(1-frontend_fee[j])
                            goals_list[j][i][2] = goals_list[j][i][0] - goals_list[j][i][1]
                            if goals_list[j][i][2] < 0.1:
                                goals_list[j][i][4] = 1.
                                achieved_goals += 1
                                target_met[j] = 1
                            else:
                                total_ai_shortfall[i] += goals_list[j][i][2]

                surplus_to_per_goal = 0
                count = int(0)
                for j in range(max(processed_goals, achieved_goals), number_of_goals):
                    if goals_list[j][i][4] < 0.1:
                        count += 1

                total_ai_remaining = total_ai_surplus[i]
                while total_ai_remaining > 0.1 and count >= 1:
                    surplus_to_per_goal = total_ai_remaining/count
                    for j in range(min(processed_goals, achieved_goals), number_of_goals):
                        if goals_list[j][i][2] > 0.1:
                            if goals_list[j][i][1] + surplus_to_per_goal* (1-frontend_fee[j]) \
                                                        >= goals_list[j][i][0]:
                                goals_list[j][i][3] = goals_list[j][i][1] + surplus_to_per_goal* \
                                                        (1-frontend_fee[j]) - goals_list[j][i][0]
                                goals_list[j][i][1] = goals_list[j][i][0]
                                goals_list[j][i][4] = 1.
                                goals_list[j][i][5] += surplus_to_per_goal* frontend_fee[j]
                                total_ai_remaining = total_ai_remaining - \
                                                        surplus_to_per_goal + goals_list[j][i][3]
                                count -= 1
                            else:
                                goals_list[j][i][1] += surplus_to_per_goal* (1-frontend_fee[j])
                                goals_list[j][i][2] = goals_list[j][i][0]- goals_list[j][i][1]
                                goals_list[j][i][5] += surplus_to_per_goal* frontend_fee[j]
                                goals_list[j][i][4] = 1 if goals_list[j][i][2] < 0.1 else 0
                                total_ai_remaining = total_ai_remaining - surplus_to_per_goal
                total_ai_surplus[i] = total_ai_remaining

    shortfall_list, surplus_list = pp.getting_shortfall_surplus(
        6, goals, years, ir_per_goal, goals_list, target_met, max_frontend_fee)
    probs_list = hp.probability_of_goals(goals, years, ir_per_goal, sigma, goals_list, surplus_list)

    return target_met, shortfall_list, surplus_list, probs_list, goals_list
