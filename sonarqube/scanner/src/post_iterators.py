#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 14:45:53 2018

@author: liujin
"""
import math
import itertools
import operator
import numpy as np
import helpers as hp
import core as cal

def adjusting_goals_iter(
        priority,
        goals,
        goal_priority,
        years,
        initial_investment,
        annual_investment,
        ir_per_goal,
        sigma,
        frontend_fee,
        backend_fee,
        target_met,
        shortfall_list):
    """
    This function is to adjust the amount of goals to make all goals being achieved
    """
    goals_adjusted_temp = goals.copy()
    backend_fee_temp = list(map(lambda x: 1-x, backend_fee))
    goals_adjusted = list(map(operator.mul, goals, backend_fee_temp))
    while not np.array(target_met).all():
        k = list(target_met).index(0)
        if shortfall_list[k] < 0.1:
            target_met[k] = 1
            shortfall_list[k] = 0
            continue
        else:
            goals_adjusted_temp[k] = goals_adjusted_temp[k] - shortfall_list[k]

            if priority == 1:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_equal(goals_adjusted_temp, years, \
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 2:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_priority(goals_adjusted_temp, goal_priority,\
                            years, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 3:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_equal(goals_adjusted_temp, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 4:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_priority(goals_adjusted_temp, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 5:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_equal_ai_priority(goals_adjusted_temp, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 6:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_priority_ai_equal(goals_adjusted_temp, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            else: print('Invalid priority number, please try again !')

    goals_adjusted = list(map(operator.mul, goals_adjusted_temp, backend_fee_temp))
    return target_met, shortfall_list, surplus_list, probs_list, goals_list, goals_adjusted

def adjusting_years_iter(
        priority,
        goals,
        goal_priority,
        years,
        initial_investment,
        annual_investment,
        ir_per_goal,
        sigma,
        frontend_fee,
        target_met,
        shortfall_list):
    """
    This function is to adjust the years of goals to make all goals being achieved
    """
    years_adjusted = years.copy()
    while not np.array(target_met).all():
        k = list(target_met).index(0)

        if shortfall_list[k] < 0.1:
            target_met[k] = 1
            shortfall_list[k] = 0
            continue
        else:
            if k == len(goals)-1:
                years_adjusted[k] += 1
            else:
                if years_adjusted[k] < years_adjusted[k+1]:
                    years_adjusted[k] += 1
                    for i in range(len(goals)-1):
                        if years_adjusted[i] == years_adjusted[i+1]:
                            years_adjusted[i+1] += 1

            if priority == 1:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_equal(goals, years_adjusted, annual_investment,\
                            ir_per_goal, frontend_fee, sigma)
            elif priority == 2:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_priority(goals, goal_priority, years_adjusted,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 3:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_equal(goals, years_adjusted, initial_investment,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 4:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_priority(goals, goal_priority, years_adjusted,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 5:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_equal_ai_priority(goals, goal_priority, years_adjusted,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 6:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_priority_ai_equal(goals, goal_priority, years_adjusted,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            else: print('Invalid priority number, please try again !')

    return target_met, shortfall_list, surplus_list, probs_list, goals_list, years_adjusted

def adjusting_annual_investment(
        priority,
        goals,
        goal_priority,
        years,
        initial_investment,
        annual_investment,
        ir_per_goal,
        sigma,
        frontend_fee,
        target_met,
        shortfall_list):
    """
    This function is to adjust the annual investment to make all goals being achieved
    """
    while not np.array(target_met).all():
        k = list(target_met).index(0)
        if shortfall_list[k] < 0.1:
            target_met[k] = 1
            shortfall_list[k] = 0
            continue
        else:
            temp = hp.calculate_pv(shortfall_list[k], years[k], ir_per_goal[k])
            temp1 = ((temp * (1 + ir_per_goal[k])) * (1 - (1 / (1 + ir_per_goal[k])))) / (1 - \
                        math.pow((1 / (1 + ir_per_goal[k])), years[k]))
            annual_investment = annual_investment + temp1
            if priority == 1:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_equal(goals, years, annual_investment, ir_per_goal,\
                            frontend_fee, sigma)
            elif priority == 2:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_priority(goals, goal_priority, years,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 3:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_equal(goals, years, initial_investment,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 4:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_priority(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 5:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_equal_ai_priority(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 6:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_priority_ai_equal(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            else: print('Invalid priority number, please try again !')
    return target_met, shortfall_list, surplus_list, probs_list, goals_list, annual_investment

def adjusting_initial_investment(
        priority,
        goals,
        goal_priority,
        years,
        initial_investment,
        annual_investment,
        ir_per_goal,
        sigma,
        frontend_fee,
        target_met,
        shortfall_list):
    """
    This function is to adjust the initial investment to make all goals being achieved
    """
    while not np.all(target_met).all():
        k = list(target_met).index(0)
        if shortfall_list[k] < 0.1:
            target_met[k] = 1
            shortfall_list[k] = 0
            continue
        else:
            temp = hp.calculate_pv(shortfall_list[k], years[k], ir_per_goal[k])
            temp1 = ((temp * (1 + ir_per_goal[k])) * (1 - (1 / (1 + ir_per_goal[k])))) / (1 - \
                        math.pow((1 / (1 + ir_per_goal[k])), years[k]))
            initial_investment = initial_investment + temp1

            if priority == 3:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_equal(goals, years, initial_investment,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 4:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_priority(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 5:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_equal_ai_priority(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 6:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_priority_ai_equal(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            else:
                print('This priority does not have initial investment, please try again !')

    return target_met, shortfall_list, surplus_list, probs_list, goals_list, initial_investment

def adjusting_irs_iter(
        priority,
        goals,
        goal_priority,
        years,
        ir_per_goal,
        target_met,
        shortfall_list,
        surplus_list,
        annual_investment,
        initial_investment,
        frontend_fee,
        manage_fee,
        sigma):
    """
    This function is to adjust the annual return to make all goals being achieved
    """
    while not np.array(target_met).all():
        k = list(target_met).index(0)
        if shortfall_list[k] < 0.1:
            target_met[k] = 1
            shortfall_list[k] = 0
            continue
        else:

            temp = hp.calculate_pv(goals[k] - shortfall_list[k], years[k]-1, ir_per_goal[k])

            temp1 = hp.calculate_ir(goals[k], temp, years[k]-1)
            ir_per_goal[k] = temp1

            if priority == 1:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_equal(goals, years, annual_investment,\
                            ir_per_goal, frontend_fee, sigma)
            elif priority == 2:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_priority(goals, goal_priority, years,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 3:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_equal(goals, years, initial_investment,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 4:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_priority(goals, goal_priority, years, \
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 5:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_equal_ai_priority(goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 6:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_priority_ai_equal(goals, goal_priority, years, \
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            else: print('Invalid priority number, please try again !')
    ir_adjusted = np.array(ir_per_goal)+manage_fee
    return ir_adjusted, goals_list, target_met, shortfall_list, \
            surplus_list, probs_list, annual_investment

def adjusting_goal_priority(
        priority,
        goals,
        years,
        target_met,
        annual_investment,
        initial_investment,
        ir_per_goal,
        sigma,
        frontend_fee,
        shortfall_list,
        surplus_list,
        probs_list):
    """
    This function is to adjust the goall priority to maximize goals being achieved
    """
    number_of_goals = len(goals)
    target_met_list = []
    target_met_ = []
    count = []
    shortfall_sum = 0
    iter_list = list(itertools.permutations(range(1, number_of_goals+1), number_of_goals))

    for k in iter_list:
        goal_priority_temp = list(k)
        if priority == 2:
            target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                cal.calculator_ai_priority(goals, goal_priority_temp, years,\
                        annual_investment, ir_per_goal, frontend_fee, sigma)
        elif priority == 4:
            target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                cal.calculator_ii_ai_priority(goals, goal_priority_temp, years,\
                        initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
        elif priority == 5:
            target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                cal.calculator_ii_equal_ai_priority(goals, goal_priority_temp, years,\
                        initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
        elif priority == 6:
            target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                cal.calculator_ii_priority_ai_equal(goals, goal_priority_temp, years,\
                        initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)

        temp1 = sum(shortfall_list)
        if shortfall_sum < temp1:
            shortfall_sum = temp1

        count_temp = list(target_met).count(1)
        target_met_list.append(target_met)
        count.append(count_temp)

    target_met_max = max(count)
    print('target_met_max', target_met_max)
    #if target_met_max <= 1:
        #goal_priority_adjusted = list(range(1,number_of_goals+1))

    #else:
    target_met_count = count.count(max(count))

    if target_met_count == 1:
        max_index = count.index(target_met_max)
        goal_priority_adjusted = list(iter_list[max_index])
    else:
        k = count.count(max(count))
        a_k = np.array(count)

        target_met_ = list(np.argpartition(a_k, -k)[-k:])
        surplus_sum, r_tem = 0, 0
        for i in target_met_:
            goal_priority_adjusted_temp1 = list(iter_list[i])
            if priority == 2:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ai_priority(goals, goal_priority_adjusted_temp1, years,\
                            annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 4:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_ai_priority(goals, goal_priority_adjusted_temp1, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 5:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_equal_ai_priority(goals, goal_priority_adjusted_temp1, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
            elif priority == 6:
                target_met, shortfall_list, surplus_list, probs_list, goals_list = \
                    cal.calculator_ii_priority_ai_equal(goals, goal_priority_adjusted_temp1, years,\
                            initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)

            if target_met.all():
                temp1 = sum(surplus_list)
                if surplus_sum <= temp1:
                    surplus_sum = temp1
                    r_tem = i
            else:
                temp2 = sum(shortfall_list)
                if shortfall_sum >= temp2:
                    shortfall_sum = temp2
                    r_tem = i
        goal_priority_adjusted = list(iter_list[r_tem])

    if priority == 2:
        target_met, shortfall_list, surplus_list, probs_list, goals_list = \
            cal.calculator_ai_priority(goals, goal_priority_adjusted, years,\
                    annual_investment, ir_per_goal, frontend_fee, sigma)
    elif priority == 4:
        target_met, shortfall_list, surplus_list, probs_list, goals_list = \
            cal.calculator_ii_ai_priority(goals, goal_priority_adjusted, years,\
                    initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
    elif priority == 5:
        target_met, shortfall_list, surplus_list, probs_list, goals_list = \
            cal.calculator_ii_equal_ai_priority(goals, goal_priority_adjusted, years,\
                    initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
    elif priority == 6:
        target_met, shortfall_list, surplus_list, probs_list, goals_list = \
            cal.calculator_ii_priority_ai_equal(goals, goal_priority_adjusted, years,\
                    initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)

    return goal_priority_adjusted, goals_list, target_met, \
            shortfall_list, surplus_list, probs_list, annual_investment

def adjustments(
        priority,
        goals,
        goal_priority,
        years,
        target_met,
        annual_investment,
        initial_investment,
        ir_per_goal,
        sigma,
        frontend_fee,
        backend_fee,
        manage_fee,
        shortfall_list,
        surplus_list,
        probs_list,
        goals_list):
    """
    main function to do adjustment
    """
    if target_met.all():
        print('All the targets can be met')
    else:
        adjustment = hp.input_adjustment()

        if adjustment == 1:
            flag = 0
            for i in range(len(goals)):
                if goals[i] < shortfall_list[i]:
                    flag = 1
            if flag > 0.1:
                print('No investment is assigned to one or more goal, no need to adjust goals')
            else:
                target_met, shortfall_list, surplus_list, probs_list, goals_list, goals_adjusted = \
                    adjusting_goals_iter(priority, goals, goal_priority, years,\
                            initial_investment, annual_investment, ir_per_goal,\
                            sigma, frontend_fee, backend_fee, target_met, shortfall_list)
                print(goals_list)
                print('Adjusted goals = ', goals_adjusted)

        elif adjustment == 2:
            target_met, shortfall_list, surplus_list, probs_list, goals_list, years_adjusted = \
                adjusting_years_iter(priority, goals, goal_priority, years, initial_investment, \
                        annual_investment, ir_per_goal, sigma, frontend_fee, \
                        target_met, shortfall_list)
            print(goals_list)
            print('Adjusted years = ', years_adjusted)

        elif adjustment == 3:
            flag = 0
            for i in range(len(goals)):
                if goals[i] < shortfall_list[i]:
                    flag = 1
            if flag > 0.1:
                print('No investment is assigned to one or more goal, no need to adjust irs')
            else:
                ir_adjusted, goals_list, target_met, shortfall_list, surplus_list, \
                probs_list, annual_investment = \
                    adjusting_irs_iter(priority, goals, goal_priority, years, \
                    ir_per_goal, target_met, shortfall_list, surplus_list, annual_investment,\
                    initial_investment, frontend_fee, manage_fee, sigma)
                print(goals_list)
                print("Adjusted ir = ", ir_adjusted)

        elif adjustment == 4:
            target_met, shortfall_list, surplus_list, probs_list, goals_list, annual_investment = \
                adjusting_annual_investment(priority, goals, goal_priority, years,\
                        initial_investment, annual_investment, ir_per_goal, sigma,\
                        frontend_fee, target_met, shortfall_list)
            print(goals_list)
            print("Adjusted annual_investment = ", round(annual_investment, 4))

        elif adjustment == 5:
            if priority == 1 or priority == 2:
                print("No initial investment is assigned to this priority ! ")
            else:
                target_met, shortfall_list, surplus_list, probs_list, \
                goals_list, initial_investment = \
                    adjusting_initial_investment(priority, goals, goal_priority, years,\
                        initial_investment, annual_investment, ir_per_goal, sigma,\
                        frontend_fee, target_met, shortfall_list)
                print(goals_list)
                print('Adjusted initial investment = ', round(initial_investment, 4))

        elif adjustment == 6:
            if priority == 1 or priority == 3:
                print("No need to adjust the goal priority !")
            else:
                goal_priority_adjusted, goals_list, target_met, shortfall_list, \
                surplus_list, probs_list, annual_investment = \
                    adjusting_goal_priority(priority, goals, years,\
                        target_met, annual_investment, initial_investment, ir_per_goal,\
                        sigma, frontend_fee, shortfall_list, \
                        surplus_list, probs_list)
                print(goals_list)
                print("Adjusted goal_priority =", goal_priority_adjusted)

        else: print("Invalid adjustment number, please try again !")
