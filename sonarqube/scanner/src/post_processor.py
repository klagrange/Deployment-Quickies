#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 11:51:24 2018
@author: liujin
"""
import numpy as np
import helpers as hp

def getting_shortfall_surplus(
        priority,
        goals,
        years,
        ir_per_goal,
        goals_list,
        target_met,
        max_frontend_fee):
    """
    this function is to get the shortfall and surplus list for the goals
    """
    number_of_goals = len(goals)
    shortfall_list, surplus_list = (
        np.zeros(number_of_goals, dtype=float) for i in range(2))

    if priority == 1 or priority == 2:
        for j in range(number_of_goals):
            if target_met[j] == 0:
                if j == 0:
                    for i in range(int(years[0])):
                        shortfall_list[j] += hp.calculate_fv(
                            goals_list[j][i][2], years[j] - i - 1, ir_per_goal[j]) \
                            * (1 + max_frontend_fee)
                else:
                    for i in range(int(years[j - 1]), int(years[j])):
                        shortfall_list[j] += hp.calculate_fv(
                            goals_list[j][i][2], years[j] - i - 1, ir_per_goal[j]) \
                            * (1 + max_frontend_fee)
            if target_met[j] == 1:
                for i in range(int(years[j])):
                    if goals_list[j][i][4] > 0.1:
                        surplus_list[j] += hp.calculate_fv(
                            goals_list[j][i][3], years[j] - i - 1, ir_per_goal[j])
    else:

        for j in range(number_of_goals):
            if target_met[j] == 0:
                shortfall_list[j] = goals_list[j][int(
                    years[j]) - 1][2] * (1 + max_frontend_fee)
            elif target_met[j] == 1:
                k = list(goals_list[j][:, 4]).index(1)
                surplus_list[j] = hp.calculate_fv(
                    goals_list[j][k][3], years[j] - k - 1, ir_per_goal[j])
    return shortfall_list, surplus_list


def output_for_json(
        goals,
        goal_id,
        goal_priority,
        years,
        annual_investment,
        initial_investment,
        ir_per_goal_org,
        backend_fee,
        frontend_fee,
        manage_fee,
        sigma,
        goals_list,
        shortfall_list,
        surplus_list,
        prob_list,
        target_met):
    """
    This function aims to output results in jason format for API
    """
    output_dict = {}
    output_dict['annualInvestment'] = round(annual_investment, 4)
    output_dict['initialInvestment'] = round(initial_investment, 4)
    output_dict['goals'] = []

    for i in range(len(goals)):
        dict_temp = {}
        dict_temp['goalPriority'] = goal_priority[i]
        dict_temp['goalID'] = goal_id[i]
        dict_temp['backendFee'] = round(backend_fee[i], 4)
        dict_temp['frontendFee'] = round(frontend_fee[i], 4)
        dict_temp['manageFee'] = round(manage_fee[i], 4)
        dict_temp['goalValue'] = round(goals[i], 4)
        dict_temp['goalDuration'] = int(years[i])
        dict_temp['discreteExpectedReturn'] = round(ir_per_goal_org[i], 4)
        dict_temp['discreteStandardDeviation'] = round(sigma[i], 4)
        dict_temp['shortfall'] = round(shortfall_list[i], 4)
        dict_temp['surplus'] = round(surplus_list[i], 4)
        dict_temp['probabilityScore'] = round(prob_list[i], 6)
        if target_met[i] == 1:
            temp = True
        else:
            temp = False
        dict_temp['isAchieved'] = temp
        dict_temp['annualBreakdown'] = []

        for j in range(len(goals_list[i])):
            temp = {}
            if goals_list[i][j][4] > 0.1:
                achieve = True
            else:
                achieve = False
            temp = {
                'year': (
                    j),
                'requiredInvestment': round(
                    goals_list[i][j][0],
                    4),
                'actualInvestment': round(
                    goals_list[i][j][1],
                    4),
                'shortfall': round(
                    goals_list[i][j][2],
                    4),
                'surplus': round(
                    goals_list[i][j][3],
                    4),
                'isAchieved': achieve,
                'frontendFee': round(
                    goals_list[i][j][5],
                    4)}
            dict_temp['annualBreakdown'].append(temp)
        output_dict['goals'].append(dict_temp)
    return output_dict
